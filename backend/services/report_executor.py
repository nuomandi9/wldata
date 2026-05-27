"""Execute admin-authored report templates safely.

A `ReportTemplate` row contains:
  - `sql_template`: parameterized SQL with `:param_name` placeholders. Admin-trusted.
  - `params_schema`: list of {name, label, type, required, default} for params bound at execution.
  - `columns_schema`: list of {key, label, type} describing output columns (key matches SQL alias).

The executor:
  - validates/coerces incoming parameter values against `params_schema`,
  - binds them via SQLAlchemy `text()` — never string-formats user input,
  - paginates by wrapping the template as a subquery,
  - returns rows as list of dicts keyed by column.key (only declared columns are exposed).

A template must NOT contain LIMIT/OFFSET; pagination is applied externally.
Templates SHOULD include a stable, total ORDER BY: pagination wraps the
template as a subquery, and PostgreSQL preserves the inner ORDER BY through
the wrap, but a template without a deterministic order can return rows in an
arbitrary (and across-page-inconsistent) sequence.
"""
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


# Hard cap on rows an export may materialize, to protect the backend from an
# unbounded query (e.g. a date range spanning the whole table). The §十 50MB
# limit governs *uploads*; this is the analogous guard for *output*.
MAX_EXPORT_ROWS = 50000


class ParamError(ValueError):
    """User-facing parameter validation error."""


class ResultTooLargeError(Exception):
    """Export result exceeds MAX_EXPORT_ROWS — user must narrow the query."""


@dataclass
class ExecutionResult:
    columns: list[dict]              # echo of columns_schema (key/label/type)
    rows: list[dict[str, Any]]       # each row keyed by column.key
    total: int                       # total matching rows (across all pages)
    page: int
    page_size: int


async def execute(
    template,
    raw_params: dict[str, Any],
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
) -> ExecutionResult:
    bound = _coerce_params(template.params_schema, raw_params)
    inner = template.sql_template.strip().rstrip(";")

    page = max(1, page)
    page_size = max(1, min(page_size, 1000))
    offset = (page - 1) * page_size

    paged_sql = f"SELECT * FROM ({inner}) AS _r LIMIT :_limit OFFSET :_offset"
    count_sql = f"SELECT COUNT(*) FROM ({inner}) AS _r"

    paged_params = {**bound, "_limit": page_size, "_offset": offset}

    rows_result = await db.execute(text(paged_sql), paged_params)
    count_result = await db.execute(text(count_sql), bound)
    total = int(count_result.scalar() or 0)

    column_keys = [c["key"] for c in template.columns_schema]
    rows: list[dict] = []
    for row in rows_result.mappings().all():
        rows.append({k: _serialize(row.get(k)) for k in column_keys})

    return ExecutionResult(
        columns=list(template.columns_schema),
        rows=rows,
        total=total,
        page=page,
        page_size=page_size,
    )


async def execute_all(template, raw_params: dict[str, Any], db: AsyncSession):
    """Fetch all matching rows for export (no pagination), capped at MAX_EXPORT_ROWS.

    Fetches one row past the cap so overflow is detected in a single query;
    raises ResultTooLargeError if the result would exceed the cap.
    Returns (columns, rows).
    """
    bound = _coerce_params(template.params_schema, raw_params)
    inner = template.sql_template.strip().rstrip(";")
    capped_sql = f"SELECT * FROM ({inner}) AS _r LIMIT :_limit"
    result = await db.execute(text(capped_sql), {**bound, "_limit": MAX_EXPORT_ROWS + 1})

    column_keys = [c["key"] for c in template.columns_schema]
    mappings = result.mappings().all()
    if len(mappings) > MAX_EXPORT_ROWS:
        raise ResultTooLargeError(
            f"导出行数超过上限 {MAX_EXPORT_ROWS}，请缩小日期范围或增加筛选条件后重试"
        )
    rows = [{k: _serialize(row.get(k)) for k in column_keys} for row in mappings]
    return list(template.columns_schema), rows


def _coerce_params(schema: list[dict], raw: dict[str, Any]) -> dict[str, Any]:
    """Convert raw param values to typed values declared in schema.

    Only declared params survive — extra keys in `raw` are discarded so they
    cannot affect the bound query in any way.
    """
    out: dict[str, Any] = {}
    for spec in schema:
        name = spec["name"]
        typ = spec.get("type", "str")
        required = bool(spec.get("required"))
        default = spec.get("default")

        value = raw.get(name)
        if value in (None, ""):
            value = default

        if value in (None, ""):
            if required:
                raise ParamError(f"参数 {spec.get('label') or name} 必填")
            out[name] = None
            continue

        try:
            out[name] = _coerce_one(typ, value)
        except (TypeError, ValueError):
            raise ParamError(
                f"参数 {spec.get('label') or name} 格式错误（期望 {typ}）"
            )
    return out


def _coerce_one(typ: str, value: Any) -> Any:
    if typ == "str":
        return str(value)
    if typ == "int":
        if isinstance(value, bool):
            raise ValueError("expected int")
        return int(value)
    if typ == "float":
        return float(value)
    if typ == "date":
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, date):
            return value
        return datetime.strptime(str(value), "%Y-%m-%d").date()
    raise ValueError(f"未知参数类型 {typ}")


def _serialize(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value
