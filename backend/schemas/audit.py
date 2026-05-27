from datetime import datetime
from typing import Any

from pydantic import BaseModel


class AuditLogOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    user_id: int | None = None
    username: str | None = None
    action: str
    target_type: str | None = None
    target_id: str | None = None
    detail: dict[str, Any] = {}
    ip: str | None = None
    created_at: datetime
