"""Pydantic schemas for the report querying API."""
from typing import Any

from pydantic import BaseModel, Field


class ReportColumnSchema(BaseModel):
    key: str
    label: str
    type: str = "str"          # str | int | float | date | datetime


class ReportParamSchema(BaseModel):
    name: str
    label: str
    type: str = "str"          # str | int | float | date
    required: bool = False
    default: Any | None = None
    # UI hints — backend ignores these, frontend uses them to render inputs:
    widget: str | None = None        # date | select | input (default)
    options_api: str | None = None   # for widget=select, FK options endpoint


class ReportTemplateInfo(BaseModel):
    key: str
    name: str
    description: str | None = None
    params_schema: list[ReportParamSchema] = Field(default_factory=list)
    columns_schema: list[ReportColumnSchema] = Field(default_factory=list)


class ReportExecuteRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)
    page: int = 1
    page_size: int = 50


class ReportExecuteResponse(BaseModel):
    columns: list[ReportColumnSchema]
    rows: list[dict[str, Any]]
    total: int
    page: int
    page_size: int


class ReportExportRequest(BaseModel):
    params: dict[str, Any] = Field(default_factory=dict)
