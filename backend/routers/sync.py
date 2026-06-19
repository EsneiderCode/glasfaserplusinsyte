import asyncio
import json
from fastapi import APIRouter, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Order, Master, OrderBoletin
from services.sync import run_sync, get_sync_state, _build_label_lookup, _safe_int, _resolve, _enrich_from_boletin_task

router = APIRouter(prefix="/api/sync")


@router.post("")
async def trigger_sync(background_tasks: BackgroundTasks):
    state = get_sync_state()
    if state["running"]:
        return {"status": "already_running", "message": "Sincronizacion ya en curso"}
    background_tasks.add_task(run_sync)
    return {"status": "started", "message": "Sincronizacion iniciada"}


@router.get("/status")
def sync_status():
    return get_sync_state()


@router.get("/progress")
async def sync_progress():
    """SSE endpoint to stream sync progress."""
    async def event_generator():
        while True:
            state = get_sync_state()
            data = json.dumps(state)
            yield f"data: {data}\n\n"
            if not state["running"] and state["status"] in ("completed", "error", "idle"):
                await asyncio.sleep(1)
                yield f"data: {data}\n\n"
                break
            await asyncio.sleep(0.5)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/fix-labels")
def fix_labels(db: Session = Depends(get_db)):
    """Resolve _label fields for all existing orders using stored masters."""
    masters_rows = db.query(Master).all()
    masters = {}
    for m in masters_rows:
        try:
            masters[m.key] = json.loads(m.data_json)
        except Exception:
            pass

    if not masters:
        return {"updated": 0, "message": "No masters found in DB"}

    lk = _build_label_lookup(masters)

    FIELD_MAP = [
        ("origen_label",            "origen_master",            "origen"),
        ("priority_label",          "priority_master",          "priority"),
        ("appoin_status_label",     "Appoin_status_master",     "appoin_status"),
        ("appoin_subco_label",      "Appoin_subco_master",      "appoin_subco"),
        ("workgroup_label",         "workgroups_master",        "workgroup"),
        ("hc_status_label",         "HC_status_master",         "hc_status"),
        ("install_status_label",    "install_status_master",    "install_status"),
        ("insyte_status_label",     "insyte_status_master",     "insyte_status"),
        ("deploy_status_label",     "deployment_status_master", "deploy_status"),
        ("operational_status_label","operational_status_master","operational_status"),
        ("pop_status_label",        "POP_status_master",        "pop_status"),
        ("approve_status_label",    "approve_status_master",    "approve_status"),
        ("ticket_status_label",     "ticket_status_master",     "ticket_status"),
        ("building_type_label",     "building_type_master",     "building_type"),
    ]

    updated = 0
    batch_size = 200
    offset = 0
    while True:
        orders = db.query(Order).offset(offset).limit(batch_size).all()
        if not orders:
            break
        for order in orders:
            for label_field, master_key, id_field in FIELD_MAP:
                id_val = getattr(order, id_field, None)
                if id_val is not None:
                    label = _resolve(lk, master_key, id_val)
                    if label:
                        setattr(order, label_field, label)
        db.commit()
        updated += len(orders)
        offset += batch_size

    return {"updated": updated, "message": f"Labels resueltos para {updated} ordenes"}


@router.post("/fix-boletin")
def fix_boletin_fields(db: Session = Depends(get_db)):
    """Backfill order fields (hc_status, install_status, priority, phone, mail, etc.)
    from already-synced boletin data. Run once to fix existing records."""
    masters_rows = db.query(Master).all()
    masters = {}
    for m in masters_rows:
        try:
            masters[m.key] = json.loads(m.data_json)
        except Exception:
            pass

    lk = _build_label_lookup(masters)

    updated = 0
    batch_size = 200
    offset = 0
    while True:
        boletins = db.query(OrderBoletin).offset(offset).limit(batch_size).all()
        if not boletins:
            break
        for boletin in boletins:
            if not boletin.raw_json:
                continue
            try:
                boletin_data = json.loads(boletin.raw_json)
            except Exception:
                continue
            task = boletin_data.get("tabTask", {}).get("task", {})
            if not task:
                continue
            order = db.get(Order, boletin.order_id)
            if order:
                _enrich_from_boletin_task(order, task, lk)
                updated += 1
        db.commit()
        offset += batch_size

    return {"updated": updated, "message": f"Campos de boletin aplicados a {updated} ordenes"}
