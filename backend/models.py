from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    address_id = Column(String, index=True)
    name = Column(String)
    phone = Column(String)
    mail = Column(String)
    origen = Column(String, index=True)
    origen_label = Column(String)
    priority = Column(Integer)
    priority_label = Column(String)
    appoin_status = Column(Integer, index=True)
    appoin_status_label = Column(String)
    appoin_date = Column(String, index=True)
    appoin_slot = Column(String)
    appoin_team = Column(String)
    appoin_subco = Column(Integer)
    appoin_subco_label = Column(String)
    workgroup = Column(Integer, index=True)
    workgroup_label = Column(String)
    hc_status = Column(Integer)
    hc_status_label = Column(String)
    install_status = Column(Integer)
    install_status_label = Column(String)
    insyte_status = Column(Integer)
    insyte_status_label = Column(String)
    deploy_status = Column(Integer)
    deploy_status_label = Column(String)
    operational_status = Column(Integer)
    operational_status_label = Column(String)
    pop_status = Column(Integer)
    pop_status_label = Column(String)
    approve_status = Column(Integer)
    approve_status_label = Column(String)
    ticket_status = Column(Integer)
    ticket_status_label = Column(String)
    building_type = Column(Integer)
    building_type_label = Column(String)
    classification = Column(String, nullable=True, index=True)
    classification_note = Column(Text, nullable=True)
    parent_order_id = Column(Integer, ForeignKey("orders.id"), nullable=True, index=True)
    # Fields extracted from boletin task (to avoid loading raw boletin on every list request)
    home_id = Column(String, nullable=True)
    city = Column(String, nullable=True)
    area = Column(String, nullable=True)
    state = Column(String, nullable=True)
    street = Column(String, nullable=True)
    full_address = Column(String, nullable=True)
    dp = Column(String, nullable=True)
    pop_code = Column(String, nullable=True)
    hz = Column(String, nullable=True)
    hzz = Column(String, nullable=True)
    building_hp = Column(String, nullable=True)
    building_wo = Column(String, nullable=True)
    insyte_notes = Column(Text, nullable=True)
    approve_notes = Column(Text, nullable=True)
    approve_work = Column(String, nullable=True)
    work_type = Column(String, nullable=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    details = relationship("OrderDetail", back_populates="order", uselist=False, cascade="all, delete-orphan")
    files = relationship("OrderFile", back_populates="order", cascade="all, delete-orphan")
    events = relationship("OrderEvent", back_populates="order", cascade="all, delete-orphan")
    tabs = relationship("OrderTab", back_populates="order", cascade="all, delete-orphan")
    history = relationship("OrderHistory", back_populates="order", cascade="all, delete-orphan")
    notes = relationship("OrderNote", back_populates="order", cascade="all, delete-orphan")
    materials = relationship("OrderMaterial", back_populates="order", cascade="all, delete-orphan")
    boletin = relationship("OrderBoletin", back_populates="order", uselist=False, cascade="all, delete-orphan")


class OrderDetail(Base):
    __tablename__ = "order_details"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="details")


class OrderFile(Base):
    __tablename__ = "order_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    remote_id = Column(String)
    filename = Column(String)
    local_path = Column(String)
    remote_url = Column(String)
    file_type = Column(String)
    file_size = Column(Integer)
    downloaded = Column(Boolean, default=False)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="files")


class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="events")


class OrderTab(Base):
    __tablename__ = "order_tabs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    tab_key = Column(String)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="tabs")


class OrderHistory(Base):
    __tablename__ = "order_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="history")


class OrderNote(Base):
    __tablename__ = "order_notes"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="notes")


class OrderMaterial(Base):
    __tablename__ = "order_materials"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), index=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="materials")


class OrderBoletin(Base):
    __tablename__ = "order_boletin"

    id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True)
    raw_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="boletin")


class Master(Base):
    __tablename__ = "masters"

    key = Column(String, primary_key=True)
    data_json = Column(Text)
    synced_at = Column(DateTime, default=datetime.utcnow)


class SyncLog(Base):
    __tablename__ = "sync_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, default="running")  # running, completed, error
    orders_synced = Column(Integer, default=0)
    files_downloaded = Column(Integer, default=0)
    error_msg = Column(Text, nullable=True)
