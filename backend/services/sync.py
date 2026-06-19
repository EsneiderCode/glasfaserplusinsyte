import json
import asyncio
import base64
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from database import SessionLocal
from models import Order, OrderHistory, OrderBoletin, Master, SyncLog
from services.portal_client import portal_client

# Shared state for progress tracking
_sync_state = {
    "running": False,
    "status": "idle",
    "orders_synced": 0,
    "files_downloaded": 0,
    "total_orders": 0,
    "current_order": None,
    "message": "",
    "error": None,
}


def get_sync_state() -> dict:
    return dict(_sync_state)


def _safe_int(val):
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _build_label_lookup(masters: dict) -> dict:
    """Build {master_key: {id: label}} from masters API response."""
    lookup = {}
    for key, val in masters.items():
        if not isinstance(val, dict):
            continue
        items = val.get("maestroData") or val.get("maestroDataEnabled") or []
        lookup[key] = {item["id"]: item.get("label", "") for item in items if "id" in item}
    return lookup


def _resolve(lookup: dict, master_key: str, val) -> Optional[str]:
    if val is None:
        return None
    id_val = _safe_int(val)
    if id_val is None:
        return None
    return lookup.get(master_key, {}).get(id_val)


def _enrich_from_boletin_task(order: Order, task: dict, label_lookup: dict):
    """Update order fields that come from boletin task, not buscador list."""
    order.hc_status = _safe_int(task.get("HC_Status"))
    order.hc_status_label = _resolve(label_lookup, "HC_status_master", task.get("HC_Status"))
    order.install_status = _safe_int(task.get("Install_Status"))
    order.install_status_label = _resolve(label_lookup, "install_status_master", task.get("Install_Status"))
    order.priority = _safe_int(task.get("Priority"))
    order.priority_label = _resolve(label_lookup, "priority_master", task.get("Priority"))
    order.operational_status = _safe_int(task.get("Operational_Status"))
    order.operational_status_label = _resolve(label_lookup, "operational_status_master", task.get("Operational_Status"))
    order.deploy_status = _safe_int(task.get("Deployment_Status"))
    order.deploy_status_label = _resolve(label_lookup, "deployment_status_master", task.get("Deployment_Status"))
    order.pop_status = _safe_int(task.get("POP_Status"))
    order.pop_status_label = _resolve(label_lookup, "POP_status_master", task.get("POP_Status"))
    order.ticket_status = _safe_int(task.get("ticket_status"))
    order.ticket_status_label = _resolve(label_lookup, "ticket_status_master", task.get("ticket_status"))
    order.building_type = _safe_int(task.get("Building_type"))
    order.building_type_label = _resolve(label_lookup, "building_type_master", task.get("Building_type"))
    phone = str(task.get("Phone") or "").strip()
    order.phone = phone or None
    mail = str(task.get("Mail") or "").strip()
    order.mail = mail or None
    # Store boletin-derived display fields as columns (avoids loading raw boletin on every list)
    order.home_id = str(task.get("Home_ID") or "").strip() or None
    order.city = str(task.get("City") or "").strip() or None
    order.area = str(task.get("Area") or "").strip() or None
    order.state = str(task.get("State") or "").strip() or None
    order.street = str(task.get("Street") or "").strip() or None
    order.dp = str(task.get("DP") or "").strip() or None
    order.pop_code = str(task.get("POP") or "").strip() or None
    order.hz = str(task.get("HZ") or "").strip() or None
    order.hzz = str(task.get("HZZ") or "").strip() or None
    # Build full address: Street + HZ + HZZ, City
    # First try Schedule second line, fallback to building from components
    schedule = str(task.get("Schedule") or "")
    schedule_lines = [l.strip() for l in schedule.split("\n") if l.strip()]
    schedule_addr = schedule_lines[1] if len(schedule_lines) > 1 else None
    # Use schedule address only if it includes the house number
    if schedule_addr and order.hz and order.hz in schedule_addr:
        order.full_address = schedule_addr
    elif order.street:
        parts = [order.street]
        if order.hz:
            parts.append(order.hz + (order.hzz or ""))
        city = str(task.get("City") or "").strip()
        addr = " ".join(parts)
        if city:
            addr += ", " + city
        order.full_address = addr
    else:
        order.full_address = schedule_addr
    order.building_hp = str(task.get("Building_HP") or "").strip() or None
    order.building_wo = str(task.get("Building_WO") or "").strip() or None
    order.insyte_notes = str(task.get("insyte_notes") or "").strip() or None
    order.approve_notes = str(task.get("approve_notes") or "").strip() or None
    order.approve_work = str(task.get("estado_aprobacion_trabajo") or "").strip() or None
    order.work_type = str(task.get("work_type_id") or "").strip() or None


def _extract_order_fields(raw: dict, label_lookup: dict = None) -> dict:
    """Map buscador item fields to Order model fields, resolving labels from masters."""
    lk = label_lookup or {}
    origen_id = _safe_int(raw.get("id_origen"))
    return {
        "id": _safe_int(raw.get("id")),
        "address_id": raw.get("address_id") or raw.get("DT_addressId"),
        "name": raw.get("name") or raw.get("DT_name"),
        "phone": raw.get("phone") or raw.get("DT_phone"),
        "mail": raw.get("mail") or raw.get("DT_mail"),
        "origen": str(raw.get("id_origen") or ""),
        "origen_label": _resolve(lk, "origen_master", origen_id),
        "priority": _safe_int(raw.get("priority")),
        "priority_label": _resolve(lk, "priority_master", raw.get("priority")),
        "appoin_status": _safe_int(raw.get("appoin_status")),
        "appoin_status_label": _resolve(lk, "Appoin_status_master", raw.get("appoin_status")),
        "appoin_date": str(raw.get("appoin_date") or ""),
        "appoin_slot": str(raw.get("appoin_slot") or ""),
        "appoin_team": raw.get("appoin_team"),
        "appoin_subco": _safe_int(raw.get("appoin_subco")),
        "appoin_subco_label": _resolve(lk, "Appoin_subco_master", raw.get("appoin_subco")),
        "workgroup": _safe_int(raw.get("id_workgroup")),
        "workgroup_label": _resolve(lk, "workgroups_master", raw.get("id_workgroup")),
        "hc_status": _safe_int(raw.get("hc_status")),
        "hc_status_label": _resolve(lk, "HC_status_master", raw.get("hc_status")),
        "install_status": _safe_int(raw.get("install_status")),
        "install_status_label": _resolve(lk, "install_status_master", raw.get("install_status")),
        "insyte_status": _safe_int(raw.get("insyte_status")),
        "insyte_status_label": _resolve(lk, "insyte_status_master", raw.get("insyte_status")),
        "deploy_status": _safe_int(raw.get("deployment_status")),
        "deploy_status_label": _resolve(lk, "deployment_status_master", raw.get("deployment_status")),
        "operational_status": _safe_int(raw.get("operational_status")),
        "operational_status_label": _resolve(lk, "operational_status_master", raw.get("operational_status")),
        "pop_status": _safe_int(raw.get("pop_status")),
        "pop_status_label": _resolve(lk, "POP_status_master", raw.get("pop_status")),
        "approve_status": _safe_int(raw.get("approve_status")),
        "approve_status_label": _resolve(lk, "approve_status_master", raw.get("approve_status")),
        "ticket_status": _safe_int(raw.get("ticket_status")),
        "ticket_status_label": _resolve(lk, "ticket_status_master", raw.get("ticket_status")),
        "building_type": _safe_int(raw.get("building_type")),
        "building_type_label": _resolve(lk, "building_type_master", raw.get("building_type")),
        "raw_json": json.dumps(raw, default=str),
        "synced_at": datetime.utcnow(),
    }


def _upsert_order(db: Session, fields: dict):
    order_id = fields.get("id")
    if order_id is None:
        return None
    existing = db.get(Order, order_id)
    if existing:
        for k, v in fields.items():
            setattr(existing, k, v)
    else:
        existing = Order(**fields)
        db.add(existing)
    db.flush()
    return existing


async def _save_boletin_photos(order_id: int, photos: list):
    """Extract base64 photos from boletin and save to files dir."""
    from config import FILES_DIR
    import aiofiles

    saved = 0
    order_dir = FILES_DIR / str(order_id)
    order_dir.mkdir(parents=True, exist_ok=True)

    for i, photo in enumerate(photos):
        img_data = photo.get("image", "")
        if not img_data or not img_data.startswith("data:"):
            continue
        try:
            header, b64data = img_data.split(",", 1)
            ext = "jpg"
            if "png" in header:
                ext = "png"
            elif "gif" in header:
                ext = "gif"
            filename = f"photo_{photo.get('id', i)}.{ext}"
            filepath = order_dir / filename
            if not filepath.exists():
                async with aiofiles.open(filepath, "wb") as f:
                    await f.write(base64.b64decode(b64data))
                saved += 1
        except Exception:
            pass
    return saved


def apply_grouping(db: Session):
    """Group orders by address_id: lowest id = parent, rest = sub-orders (oldest first)."""
    from sqlalchemy import func
    # Reset all grouping first
    db.query(Order).update({"parent_order_id": None}, synchronize_session=False)
    # Find parent (min id) for each address_id with more than one order
    rows = (
        db.query(Order.address_id, func.min(Order.id).label("parent_id"))
        .filter(Order.address_id != None, Order.address_id != "")
        .group_by(Order.address_id)
        .having(func.count(Order.id) > 1)
        .all()
    )
    for address_id, parent_id in rows:
        db.query(Order).filter(
            Order.address_id == address_id,
            Order.id != parent_id,
        ).update({"parent_order_id": parent_id}, synchronize_session=False)
    db.commit()


async def run_sync():
    if _sync_state["running"]:
        return

    _sync_state.update({
        "running": True,
        "status": "running",
        "orders_synced": 0,
        "files_downloaded": 0,
        "total_orders": 0,
        "current_order": None,
        "message": "Iniciando sincronizacion...",
        "error": None,
    })

    db = SessionLocal()
    log = SyncLog(started_at=datetime.utcnow(), status="running")
    db.add(log)
    db.commit()

    try:
        # Step 1: Masters
        _sync_state["message"] = "Descargando maestros..."
        masters = await portal_client.get_masters()
        for key, value in masters.items():
            m = db.get(Master, key)
            if m:
                m.data_json = json.dumps(value, default=str)
                m.synced_at = datetime.utcnow()
            else:
                db.add(Master(key=key, data_json=json.dumps(value, default=str)))
        db.commit()

        # Build label lookup from masters for resolving _label fields
        label_lookup = _build_label_lookup(masters)

        # Step 2: Fetch all orders with pagination
        _sync_state["message"] = "Contando ordenes..."
        first_batch = await portal_client.get_orders(first=0, rows=1)
        total = first_batch.get("total", 0)
        _sync_state["total_orders"] = total
        _sync_state["message"] = f"Descargando {total} ordenes..."

        page_size = 100
        all_items = []
        for offset in range(0, total, page_size):
            result = await portal_client.get_orders(first=offset, rows=page_size)
            batch = result.get("items", [])
            all_items.extend(batch)
            if len(batch) < page_size:
                break

        # Step 3: Process each order
        for i, raw_order in enumerate(all_items):
            fields = _extract_order_fields(raw_order, label_lookup)
            order_id = fields.get("id")
            if order_id is None:
                continue

            _sync_state["current_order"] = order_id
            _sync_state["message"] = f"Orden {order_id} ({i+1}/{len(all_items)})"

            _upsert_order(db, fields)

            # Fetch boletin and history concurrently
            boletin_data, history_data = await asyncio.gather(
                portal_client.get_order_boletin(order_id),
                portal_client.get_order_history(order_id),
                return_exceptions=True,
            )

            # Boletin
            if isinstance(boletin_data, dict) and boletin_data:
                existing = db.query(OrderBoletin).filter_by(order_id=order_id).first()
                # Keep tabPhotos metadata but strip base64 image data (images stored as files)
                boletin_no_photos = dict(boletin_data)
                if "tabPhotos" in boletin_no_photos:
                    photos_meta = [
                        {k: v for k, v in p.items() if k != "image"}
                        for p in boletin_no_photos["tabPhotos"].get("photos", [])
                    ]
                    boletin_no_photos["tabPhotos"] = {"photos": photos_meta}
                boletin_json = json.dumps(boletin_no_photos, default=str)
                if existing:
                    existing.raw_json = boletin_json
                    existing.synced_at = datetime.utcnow()
                else:
                    db.add(OrderBoletin(order_id=order_id, raw_json=boletin_json))

                # Enrich order with fields only available in boletin task
                task = boletin_data.get("tabTask", {}).get("task", {})
                if task:
                    order = db.get(Order, order_id)
                    if order:
                        _enrich_from_boletin_task(order, task, label_lookup)

                # Save photos from base64
                photos = boletin_data.get("tabPhotos", {}).get("photos", [])
                if photos:
                    saved = await _save_boletin_photos(order_id, photos)
                    _sync_state["files_downloaded"] += saved

            # History
            if isinstance(history_data, list):
                db.query(OrderHistory).filter_by(order_id=order_id).delete()
                for h in history_data:
                    db.add(OrderHistory(order_id=order_id, raw_json=json.dumps(h, default=str)))

            db.commit()
            _sync_state["orders_synced"] += 1

        _sync_state["message"] = "Agrupando ordenes por direccion..."
        apply_grouping(db)

        log.finished_at = datetime.utcnow()
        log.status = "completed"
        log.orders_synced = _sync_state["orders_synced"]
        log.files_downloaded = _sync_state["files_downloaded"]
        db.commit()

        _sync_state["status"] = "completed"
        _sync_state["message"] = (
            f"Completado: {_sync_state['orders_synced']} ordenes, "
            f"{_sync_state['files_downloaded']} fotos"
        )

    except Exception as e:
        _sync_state["status"] = "error"
        _sync_state["error"] = str(e)
        _sync_state["message"] = f"Error: {e}"
        log.status = "error"
        log.error_msg = str(e)
        log.finished_at = datetime.utcnow()
        db.commit()
    finally:
        _sync_state["running"] = False
        _sync_state["current_order"] = None
        db.close()
