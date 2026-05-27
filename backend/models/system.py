from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime, Text, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SysUser(Base):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    real_name: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="operator")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class SysAuditLog(Base):
    """Operation audit trail. One row per audited write.

    `username` is a denormalized snapshot so the trail survives even if the
    user row is later renamed; `user_id` may be NULL if the actor is gone.
    `target_id` is a string so it can reference non-integer / composite targets.
    The shape of `detail` is documented per-action in `services/audit_service.py`.
    """
    __tablename__ = "sys_audit_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("sys_user.id"))
    username: Mapped[str | None] = mapped_column(String(50))
    action: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    target_type: Mapped[str | None] = mapped_column(String(50))
    target_id: Mapped[str | None] = mapped_column(String(64))
    detail: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    ip: Mapped[str | None] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
