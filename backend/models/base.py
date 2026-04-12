from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class DictBase:
    """Mixin for all dictionary tables."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
