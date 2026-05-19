from datetime import date, datetime

from sqlalchemy import String, Date, Integer, ForeignKey, DateTime, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class DeliveryRecord(Base):
    __tablename__ = "biz_delivery_record"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    record_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    vehicle_id: Mapped[int] = mapped_column(Integer, ForeignKey("dict_vehicle.id"), nullable=False)
    driver_id: Mapped[int] = mapped_column(Integer, ForeignKey("dict_person.id"), nullable=False)
    deliverer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    route_id: Mapped[int] = mapped_column(Integer, ForeignKey("dict_route.id"), nullable=False)
    customer_count: Mapped[int | None] = mapped_column(Integer)
    delivery_count: Mapped[int | None] = mapped_column(Integer)
    remark: Mapped[str | None] = mapped_column(Text)
    warn_notes: Mapped[str | None] = mapped_column(Text)
    created_by_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sys_user.id"))
    extra: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
