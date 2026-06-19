import json
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, defer
from sqlalchemy import or_, case, func
from typing import Optional
from database import get_db
from models import Order, Master, SyncLog

router = APIRouter(prefix="/api")

CLASSIFICATION_VALUES = [
    "YA CERTIFICADOS",
    "PENDIENTES POR CERTIFICAR",
    "PENDIENTES POR REVISION",
    "DEVUELTOS",
    "POR HACER",
    "PEND POR NUEVA VISITA",
    "SIN SUBIRSE",
    "CANCELADOS",
]


class ClassificationBody(BaseModel):
    classification: Optional[str] = None
    note: Optional[str] = None


SORTABLE_FIELDS = {
    "appoin_date": Order.appoin_date,
    "appoin_slot": Order.appoin_slot,
    "name": Order.name,
    "address_id": Order.address_id,
    "appoin_status": Order.appoin_status,
    "workgroup": Order.workgroup,
    "insyte_status": Order.insyte_status,
    "approve_status": Order.approve_status,
    "install_status": Order.install_status,
    "synced_at": Order.synced_at,
}


@router.get("/orders")
def list_orders(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(200, ge=1, le=1000),
    search: Optional[str] = None,
    appoin_status: Optional[int] = None,
    priority: Optional[int] = None,
    workgroup: Optional[int] = None,
    install_status: Optional[int] = None,
    insyte_status: Optional[int] = None,
    approve_status: Optional[int] = None,
    hc_status: Optional[int] = None,
    building_type: Optional[int] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    sort_by: Optional[str] = None,
    sort_order: Optional[str] = "desc",
    hide_classified: bool = False,
    grouped: bool = False,
):
    # Exclude heavy columns not needed for the list view
    q = db.query(Order).options(defer(Order.raw_json))

    if search:
        like = f"%{search}%"
        q = q.filter(or_(
            Order.name.ilike(like),
            Order.address_id.ilike(like),
            Order.phone.ilike(like),
            Order.mail.ilike(like),
            Order.appoin_team.ilike(like),
        ))

    if appoin_status is not None:
        q = q.filter(Order.appoin_status == appoin_status)
    if priority is not None:
        q = q.filter(Order.priority == priority)
    if workgroup is not None:
        q = q.filter(Order.workgroup == workgroup)
    if install_status is not None:
        q = q.filter(Order.install_status == install_status)
    if insyte_status is not None:
        q = q.filter(Order.insyte_status == insyte_status)
    if approve_status is not None:
        q = q.filter(Order.approve_status == approve_status)
    if hc_status is not None:
        q = q.filter(Order.hc_status == hc_status)
    if building_type is not None:
        q = q.filter(Order.building_type == building_type)
    if date_from:
        q = q.filter(Order.appoin_date >= date_from)
    if date_to:
        q = q.filter(Order.appoin_date <= date_to)
    if hide_classified:
        q = q.filter(Order.classification == None)

    if grouped:
        q = q.filter(Order.parent_order_id == None)

    total = q.count()
    # Global unclassified count (not affected by filters)
    total_unclassified = db.query(func.count(Order.id)).filter(Order.classification == None).scalar()

    sort_col = SORTABLE_FIELDS.get(sort_by, Order.id)
    # Put NULL / empty-string values at the end regardless of direction
    is_empty = case((sort_col == None, 1), (sort_col == "", 1), else_=0)
    if sort_order == "asc":
        order_expr = (is_empty.asc(), sort_col.asc())
    else:
        order_expr = (is_empty.asc(), sort_col.desc())

    orders = (
        q.order_by(*order_expr)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    if grouped:
        # Count sub_orders per parent without loading full data
        sub_counts = (
            db.query(Order.parent_order_id, func.count(Order.id).label("cnt"))
            .filter(Order.parent_order_id.in_([o.id for o in orders]))
            .group_by(Order.parent_order_id)
            .all()
        ) if orders else []
        sub_count_map = {row.parent_order_id: row.cnt for row in sub_counts}
        data = []
        for o in orders:
            d = _order_to_dict(o)
            d["sub_orders"] = []  # loaded lazily on row expand
            d["sub_orders_count"] = sub_count_map.get(o.id, 0)
            data.append(d)
        return {"data": data, "total": total, "total_unclassified": total_unclassified, "page": page, "page_size": page_size}

    return {
        "data": [_order_to_dict(o) for o in orders],
        "total": total,
        "total_unclassified": total_unclassified,
        "page": page,
        "page_size": page_size,
    }


@router.get("/orders/{order_id}/sub-orders")
def get_sub_orders(order_id: int, db: Session = Depends(get_db)):
    subs = (
        db.query(Order)
        .filter(Order.parent_order_id == order_id)
        .order_by(Order.appoin_date.asc())
        .all()
    )
    return [_order_to_dict(s) for s in subs]


@router.get("/orders/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        return {"error": "Not found"}, 404

    result = _order_to_dict(order)
    result["raw_json"] = order.raw_json

    if order.details:
        result["details"] = json.loads(order.details.raw_json) if order.details.raw_json else {}

    # Build photo metadata map from boletin (fotoId, insyte_fase, fase, comment)
    foto_meta_map = {}  # photo numeric id -> metadata dict
    if order.boletin and order.boletin.raw_json:
        try:
            boletin_data = json.loads(order.boletin.raw_json)
            for p in boletin_data.get("tabPhotos", {}).get("photos", []):
                pid = p.get("id")
                if pid is not None:
                    foto_meta_map[int(pid)] = {
                        "fotoId": p.get("fotoId"),
                        "insyte_fase": p.get("insyte_fase"),
                        "fase": p.get("fase"),
                        "comment": p.get("comment"),
                        "created_at": p.get("created_at"),
                    }
        except Exception:
            pass

    # Photos stored locally in data/files/{order_id}/
    from config import FILES_DIR
    photos_dir = FILES_DIR / str(order_id)
    photos = []
    if photos_dir.exists():
        for f in sorted(photos_dir.iterdir()):
            if f.is_file():
                # Extract numeric photo id from filename: photo_26397.jpg -> 26397
                photo_id = None
                stem = f.stem
                if stem.startswith("photo_"):
                    try:
                        photo_id = int(stem[6:])
                    except ValueError:
                        pass
                meta = foto_meta_map.get(photo_id, {})
                photos.append({
                    "filename": f.name,
                    "url": f"/api/files/{order_id}/{f.name}",
                    "order_id": order_id,
                    "photo_id": photo_id,
                    "fotoId": meta.get("fotoId"),
                    "insyte_fase": meta.get("insyte_fase"),
                    "fase": meta.get("fase"),
                    "comment": meta.get("comment"),
                    "created_at": meta.get("created_at"),
                })
    result["photos"] = photos

    result["history"] = [json.loads(h.raw_json) for h in order.history if h.raw_json]

    if order.boletin and order.boletin.raw_json:
        result["boletin"] = json.loads(order.boletin.raw_json)

    return result


@router.patch("/orders/{order_id}/classification")
def set_classification(order_id: int, body: ClassificationBody, db: Session = Depends(get_db)):
    order = db.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Not found")
    if body.classification is not None and body.classification not in CLASSIFICATION_VALUES:
        raise HTTPException(status_code=400, detail=f"Invalid classification: {body.classification}")
    order.classification = body.classification
    order.classification_note = body.note if body.classification is not None else None
    db.commit()
    return {"id": order_id, "classification": order.classification, "classification_note": order.classification_note}


@router.post("/orders/regroup")
def regroup_orders(db: Session = Depends(get_db)):
    from services.sync import apply_grouping
    apply_grouping(db)
    total_sub = db.query(Order).filter(Order.parent_order_id != None).count()
    total_parent = db.query(Order).filter(Order.parent_order_id == None).count()
    return {"parents": total_parent, "sub_orders": total_sub}


class BulkClassificationBody(BaseModel):
    classification: Optional[str] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None


@router.post("/orders/bulk-classify")
def bulk_classify(body: BulkClassificationBody, db: Session = Depends(get_db)):
    if body.classification is not None and body.classification not in CLASSIFICATION_VALUES:
        raise HTTPException(status_code=400, detail=f"Invalid classification: {body.classification}")
    q = db.query(Order)
    if body.date_from:
        q = q.filter(Order.appoin_date >= body.date_from)
    if body.date_to:
        q = q.filter(Order.appoin_date <= body.date_to)
    updated = q.update({"classification": body.classification}, synchronize_session=False)
    db.commit()
    return {"updated": updated, "classification": body.classification}


@router.get("/board")
def get_board(db: Session = Depends(get_db)):
    orders = (
        db.query(Order)
        .filter(Order.classification != None)
        .order_by(Order.appoin_date.desc())
        .all()
    )
    grouped = {cat: [] for cat in CLASSIFICATION_VALUES}
    for o in orders:
        cat = o.classification
        if cat in grouped:
            grouped[cat].append(_order_to_dict(o))
    total_orders = db.query(Order).count()
    total_classified = len(orders)
    total_unclassified = total_orders - total_classified
    return {
        "grouped": grouped,
        "total_orders": total_orders,
        "total_classified": total_classified,
        "total_unclassified": total_unclassified,
    }


@router.get("/masters")
def get_masters(db: Session = Depends(get_db)):
    masters = db.query(Master).all()
    result = {}
    for m in masters:
        try:
            result[m.key] = json.loads(m.data_json)
        except Exception:
            result[m.key] = m.data_json
    return result


@router.get("/sync/logs")
def get_sync_logs(db: Session = Depends(get_db)):
    logs = db.query(SyncLog).order_by(SyncLog.started_at.desc()).limit(10).all()
    return [
        {
            "id": l.id,
            "started_at": l.started_at,
            "finished_at": l.finished_at,
            "status": l.status,
            "orders_synced": l.orders_synced,
            "files_downloaded": l.files_downloaded,
            "error_msg": l.error_msg,
        }
        for l in logs
    ]


def _order_to_dict(o: Order) -> dict:
    return {
        "id": o.id,
        "address_id": o.address_id,
        "home_id": o.home_id,
        "name": o.name,
        "phone": o.phone,
        "mail": o.mail,
        "city": o.city,
        "area": o.area,
        "state": o.state,
        "street": o.street,
        "full_address": o.full_address,
        "dp": o.dp,
        "pop": o.pop_code,
        "hz": o.hz,
        "hzz": o.hzz,
        "building_hp": o.building_hp,
        "building_wo": o.building_wo,
        "insyte_notes": o.insyte_notes,
        "approve_notes": o.approve_notes,
        "approve_work": o.approve_work,
        "work_type": o.work_type,
        "origen": o.origen,
        "origen_label": o.origen_label,
        "priority": o.priority,
        "priority_label": o.priority_label,
        "appoin_status": o.appoin_status,
        "appoin_status_label": o.appoin_status_label,
        "appoin_date": o.appoin_date,
        "appoin_slot": o.appoin_slot,
        "appoin_team": o.appoin_team,
        "appoin_subco": o.appoin_subco,
        "appoin_subco_label": o.appoin_subco_label,
        "workgroup": o.workgroup,
        "workgroup_label": o.workgroup_label,
        "hc_status": o.hc_status,
        "hc_status_label": o.hc_status_label,
        "install_status": o.install_status,
        "install_status_label": o.install_status_label,
        "insyte_status": o.insyte_status,
        "insyte_status_label": o.insyte_status_label,
        "deploy_status": o.deploy_status,
        "deploy_status_label": o.deploy_status_label,
        "operational_status": o.operational_status,
        "operational_status_label": o.operational_status_label,
        "pop_status": o.pop_status,
        "pop_status_label": o.pop_status_label,
        "approve_status": o.approve_status,
        "approve_status_label": o.approve_status_label,
        "ticket_status": o.ticket_status,
        "ticket_status_label": o.ticket_status_label,
        "building_type": o.building_type,
        "building_type_label": o.building_type_label,
        "classification": o.classification,
        "classification_note": o.classification_note,
        "parent_order_id": o.parent_order_id,
        "sub_orders_count": 0,
        "synced_at": o.synced_at.isoformat() if o.synced_at else None,
    }
