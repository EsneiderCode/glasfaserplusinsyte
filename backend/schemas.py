from pydantic import BaseModel
from typing import Any, Optional
from datetime import datetime


class OrderBase(BaseModel):
    id: int
    address_id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    mail: Optional[str] = None
    origen: Optional[str] = None
    origen_label: Optional[str] = None
    priority: Optional[int] = None
    priority_label: Optional[str] = None
    appoin_status: Optional[int] = None
    appoin_status_label: Optional[str] = None
    appoin_date: Optional[str] = None
    appoin_slot: Optional[str] = None
    appoin_team: Optional[str] = None
    appoin_subco: Optional[int] = None
    appoin_subco_label: Optional[str] = None
    workgroup: Optional[int] = None
    workgroup_label: Optional[str] = None
    hc_status: Optional[int] = None
    hc_status_label: Optional[str] = None
    install_status: Optional[int] = None
    install_status_label: Optional[str] = None
    insyte_status: Optional[int] = None
    insyte_status_label: Optional[str] = None
    deploy_status: Optional[int] = None
    deploy_status_label: Optional[str] = None
    operational_status: Optional[int] = None
    operational_status_label: Optional[str] = None
    pop_status: Optional[int] = None
    pop_status_label: Optional[str] = None
    approve_status: Optional[int] = None
    approve_status_label: Optional[str] = None
    ticket_status: Optional[int] = None
    ticket_status_label: Optional[str] = None
    building_type: Optional[int] = None
    building_type_label: Optional[str] = None
    synced_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class OrderFile(BaseModel):
    id: int
    order_id: int
    remote_id: Optional[str] = None
    filename: Optional[str] = None
    local_path: Optional[str] = None
    file_type: Optional[str] = None
    downloaded: bool = False

    class Config:
        from_attributes = True


class OrderDetail(BaseModel):
    order_id: int
    raw_json: Optional[str] = None

    class Config:
        from_attributes = True


class OrderFull(OrderBase):
    details: Optional[OrderDetail] = None
    files: list[OrderFile] = []
    events: list[Any] = []
    tabs: list[Any] = []
    history: list[Any] = []
    notes: list[Any] = []
    materials: list[Any] = []
    boletin: Optional[Any] = None
    raw_json: Optional[str] = None


class OrdersResponse(BaseModel):
    data: list[OrderBase]
    total: int
    page: int
    page_size: int


class SyncStatus(BaseModel):
    status: str
    orders_synced: int
    files_downloaded: int
    current_order: Optional[int] = None
    message: Optional[str] = None
    error: Optional[str] = None
