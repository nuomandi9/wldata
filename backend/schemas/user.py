from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

Role = Literal["admin", "operator"]


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    password: str = Field(min_length=6, max_length=128)
    real_name: str | None = Field(default=None, max_length=50)
    role: Role = "operator"


class UserUpdate(BaseModel):
    """Only these fields are mutable. Password changes go through reset-password;
    username is immutable (it is the audit-trail key)."""
    real_name: str | None = Field(default=None, max_length=50)
    role: Role | None = None
    is_active: bool | None = None


class PasswordReset(BaseModel):
    new_password: str = Field(min_length=6, max_length=128)


class UserOut(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    username: str
    real_name: str | None = None
    role: str
    is_active: bool
    created_at: datetime
