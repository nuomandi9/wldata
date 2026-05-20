"""Fixed-report API: list active templates, execute one with bound params, export to xlsx.

Templates live in `sys_report_template`. The SQL inside `sql_template` is
admin-authored and trusted; user-supplied parameters are bound via SQLAlchemy
`text()` and never interpolated.
"""
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.report import ReportTemplate
from schemas.auth import UserInfo
from schemas.report import (
    ReportExecuteRequest, ReportExecuteResponse, ReportExportRequest,
    ReportTemplateInfo,
)
from services import report_executor
from services.excel_exporter import render_xlsx


router = APIRouter(prefix="/api/report", tags=["报表查询"])


@router.get("/templates", response_model=list[ReportTemplateInfo])
async def list_templates(
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    result = await db.execute(
        select(ReportTemplate)
        .where(ReportTemplate.is_active.is_(True))
        .order_by(ReportTemplate.id)
    )
    return [_to_info(t) for t in result.scalars().all()]


@router.get("/templates/{key}", response_model=ReportTemplateInfo)
async def get_template(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    tpl = await _load_template(db, key)
    return _to_info(tpl)


@router.post("/{key}/execute", response_model=ReportExecuteResponse)
async def execute_report(
    key: str,
    body: ReportExecuteRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    tpl = await _load_template(db, key)
    try:
        result = await report_executor.execute(
            tpl, body.params, db, page=body.page, page_size=body.page_size,
        )
    except report_executor.ParamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (DBAPIError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=400, detail=f"报表执行失败：{exc.orig if hasattr(exc, 'orig') else exc}") from exc

    return ReportExecuteResponse(
        columns=result.columns,
        rows=result.rows,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


@router.post("/{key}/export")
async def export_report(
    key: str,
    body: ReportExportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    tpl = await _load_template(db, key)
    try:
        columns, rows = await report_executor.execute_all(tpl, body.params, db)
    except report_executor.ParamError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (DBAPIError, SQLAlchemyError) as exc:
        raise HTTPException(status_code=400, detail=f"报表执行失败：{exc.orig if hasattr(exc, 'orig') else exc}") from exc

    xlsx_bytes = render_xlsx(tpl.name, columns, rows)
    filename = f"{tpl.name}.xlsx"
    # RFC 5987 encoding so Chinese filenames survive the Content-Disposition header
    disposition = f"attachment; filename*=UTF-8''{quote(filename)}"
    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": disposition},
    )


# ── Internals ──

async def _load_template(db: AsyncSession, key: str) -> ReportTemplate:
    result = await db.execute(
        select(ReportTemplate).where(ReportTemplate.key == key)
    )
    tpl = result.scalar_one_or_none()
    if tpl is None or not tpl.is_active:
        raise HTTPException(status_code=404, detail="报表不存在或已停用")
    return tpl


def _to_info(tpl: ReportTemplate) -> ReportTemplateInfo:
    return ReportTemplateInfo(
        key=tpl.key,
        name=tpl.name,
        description=tpl.description,
        params_schema=tpl.params_schema or [],
        columns_schema=tpl.columns_schema or [],
    )
