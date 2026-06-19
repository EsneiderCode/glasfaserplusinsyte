import sys
import os

# Ensure backend dir is in path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from routers import orders, sync, files

app = FastAPI(title="WorkOrders Agent API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174", "http://localhost:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(sync.router)
app.include_router(files.router)


@app.on_event("startup")
def on_startup():
    init_db()
    _migrate_add_boletin_columns()
    _backfill_boletin_columns()


def _backfill_boletin_columns():
    """One-time backfill: populate new Order columns from existing boletin data."""
    import json
    from database import SessionLocal
    from models import Order, OrderBoletin, Master
    from services.sync import _build_label_lookup, _enrich_from_boletin_task

    db = SessionLocal()
    try:
        # Check if backfill is needed: any boletin exists but the order has no street
        needs_backfill = db.query(OrderBoletin).join(
            Order, Order.id == OrderBoletin.order_id
        ).filter(Order.street == None).first()
        if not needs_backfill:
            return

        masters_rows = db.query(Master).all()
        masters = {}
        for m in masters_rows:
            try:
                masters[m.key] = json.loads(m.data_json)
            except Exception:
                pass
        lk = _build_label_lookup(masters)

        batch_size = 100
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
            db.commit()
            offset += batch_size
    except Exception as e:
        print(f"Backfill warning: {e}")
    finally:
        db.close()


def _migrate_add_boletin_columns():
    """Add boletin-derived columns to orders table if they don't exist yet."""
    from database import engine
    new_cols = [
        ("home_id", "VARCHAR"),
        ("city", "VARCHAR"),
        ("area", "VARCHAR"),
        ("state", "VARCHAR"),
        ("street", "VARCHAR"),
        ("dp", "VARCHAR"),
        ("pop_code", "VARCHAR"),
        ("hz", "VARCHAR"),
        ("hzz", "VARCHAR"),
        ("building_hp", "VARCHAR"),
        ("building_wo", "VARCHAR"),
        ("insyte_notes", "TEXT"),
        ("approve_notes", "TEXT"),
        ("approve_work", "VARCHAR"),
        ("work_type", "VARCHAR"),
    ]
    with engine.connect() as conn:
        existing = {row[1] for row in conn.execute(
            __import__("sqlalchemy").text("PRAGMA table_info(orders)")
        )}
        for col_name, col_type in new_cols:
            if col_name not in existing:
                conn.execute(__import__("sqlalchemy").text(
                    f"ALTER TABLE orders ADD COLUMN {col_name} {col_type}"
                ))
        conn.commit()


@app.get("/")
def root():
    return {"status": "ok", "message": "WorkOrders Agent API running"}
