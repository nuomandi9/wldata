from datetime import date
from typing import Any

from pydantic import BaseModel


class TemplateColumnInfo(BaseModel):
    header: str
    field: str
    type: str
    required: bool


class TemplateInfo(BaseModel):
    key: str
    name: str
    description: str
    columns: list[TemplateColumnInfo]


class IssueInfo(BaseModel):
    level: str          # "BLOCK" or "WARN"
    field: str | None
    message: str


class PreviewRow(BaseModel):
    row_number: int
    raw: dict[str, Any]
    resolved: dict[str, Any]
    issues: list[IssueInfo]
    has_block: bool
    has_warn: bool


class PreviewResponse(BaseModel):
    template_key: str
    total: int
    block_count: int
    warn_count: int
    ok_count: int
    rows: list[PreviewRow]


class CommitRowInput(BaseModel):
    """A row to insert. `resolved` is the validator-produced dict; the API
    rebuilds it from the uploaded file to avoid trusting client-supplied
    FK ids."""
    row_number: int
    warn_notes: str | None = None


class CommitResponse(BaseModel):
    inserted: int
    skipped: int
    skipped_reasons: list[str] = []
