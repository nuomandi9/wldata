"""Validate parsed Excel rows against a template.

Each row passes through three stages:
  1. Type coercion + required check (BLOCK on failure).
  2. Dictionary lookup → fills in FK ids on the resolved row.
     Lookup miss = BLOCK; lookup target inactive = BLOCK (per design doc
     §5.3 — "车辆已停用" is a BLOCK, not a WARN).
  3. Numeric range check → WARN if outside warn_min/warn_max.

The validator returns one `RowValidation` per row; the API decides which
rows can be committed (no BLOCK; WARNs may be overridden with warn_notes).
"""
from dataclasses import dataclass, field
from datetime import date, datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from services.import_templates import ImportColumn, ImportTemplate, Lookup


BLOCK = "BLOCK"
WARN = "WARN"


@dataclass
class Issue:
    level: str          # "BLOCK" or "WARN"
    field: str | None
    message: str


@dataclass
class RowValidation:
    row_number: int                          # 1-based, matches Excel data row (header excluded)
    raw: dict[str, Any]                      # original parsed cells
    resolved: dict[str, Any] = field(default_factory=dict)   # ready-to-insert row
    issues: list[Issue] = field(default_factory=list)

    @property
    def has_block(self) -> bool:
        return any(i.level == BLOCK for i in self.issues)

    @property
    def has_warn(self) -> bool:
        return any(i.level == WARN for i in self.issues)


async def validate_rows(
    rows: list[dict[str, Any]],
    template: ImportTemplate,
    db: AsyncSession,
) -> list[RowValidation]:
    """Run the full validation pipeline against parsed rows.

    Dictionary lookups are cached across the batch so a 1000-row import
    that references the same 20 vehicles only hits the DB 20 times per
    column.
    """
    lookup_cache: dict[tuple[Any, str, Any], tuple[int | None, bool]] = {}
    results: list[RowValidation] = []

    for index, raw in enumerate(rows, start=1):
        rv = RowValidation(row_number=index, raw=raw)
        for col in template.columns:
            value = raw.get(col.field)
            coerced, type_issue = _coerce(col, value)
            if type_issue:
                rv.issues.append(type_issue)
                continue
            if col.required and coerced is None:
                rv.issues.append(Issue(BLOCK, col.field, f"{col.header} 必填"))
                continue
            if coerced is None:
                continue

            if col.lookup is not None:
                fk_id, lookup_issue = await _resolve_lookup(col, coerced, db, lookup_cache)
                if lookup_issue:
                    rv.issues.append(lookup_issue)
                    continue
                rv.resolved[col.lookup.out_field] = fk_id
            else:
                rv.resolved[col.field] = coerced

            range_issue = _check_range(col, coerced)
            if range_issue:
                rv.issues.append(range_issue)

        results.append(rv)

    return results


def _coerce(col: ImportColumn, value: Any) -> tuple[Any, Issue | None]:
    if value is None or value == "":
        return None, None
    try:
        if col.type == "str":
            return str(value).strip(), None
        if col.type == "int":
            if isinstance(value, bool):
                raise ValueError("expected int")
            return int(value), None
        if col.type == "float":
            return float(value), None
        if col.type == "date":
            if isinstance(value, datetime):
                return value.date(), None
            if isinstance(value, date):
                return value, None
            return datetime.strptime(str(value).strip(), "%Y-%m-%d").date(), None
    except (TypeError, ValueError):
        return None, Issue(
            BLOCK, col.field,
            f"{col.header} 格式错误（期望 {col.type}，实际：{value!r}）",
        )
    return value, None


async def _resolve_lookup(
    col: ImportColumn,
    value: Any,
    db: AsyncSession,
    cache: dict[tuple[Any, str, Any], tuple[int | None, bool]],
) -> tuple[int | None, Issue | None]:
    lookup: Lookup = col.lookup
    key = (lookup.model, lookup.by, value)
    if key not in cache:
        cache[key] = await _query_lookup(lookup, value, db)
    fk_id, is_active = cache[key]

    if fk_id is None:
        return None, Issue(
            BLOCK, col.field,
            f"{col.header} 在字典中不存在：{value!r}",
        )
    if lookup.require_active and not is_active:
        return None, Issue(
            BLOCK, col.field,
            f"{col.header} 已停用：{value!r}",
        )
    return fk_id, None


async def _query_lookup(
    lookup: Lookup, value: Any, db: AsyncSession,
) -> tuple[int | None, bool]:
    model = lookup.model
    column = getattr(model, lookup.by)
    result = await db.execute(
        select(model.id, model.is_active).where(column == value).limit(2)
    )
    rows = result.all()
    if len(rows) != 1:
        return None, False
    fk_id, is_active = rows[0]
    return fk_id, bool(is_active)


def _check_range(col: ImportColumn, value: Any) -> Issue | None:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        return None
    if col.warn_min is not None and value < col.warn_min:
        return Issue(WARN, col.field, f"{col.header} 低于预警阈值 {col.warn_min}")
    if col.warn_max is not None and value > col.warn_max:
        return Issue(WARN, col.field, f"{col.header} 高于预警阈值 {col.warn_max}")
    return None
