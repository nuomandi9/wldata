"""Audit log query API — admin only, read only.

The trail is append-only; there is no create/update/delete endpoint. Rows are
written by `services/audit_service.record()` from the audited operations.
"""
from datetime import date, datetime, time

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import require_admin
from models.system import SysAuditLog
from schemas.auth import UserInfo
from schemas.audit import AuditLogOut
from schemas.common import PageResult

router = APIRouter(prefix="/api/audit", tags=["审计日志"])


@router.get("/logs", response_model=PageResult[AuditLogOut])
async def list_logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    username: str | None = Query(None),
    action: str | None = Query(None),
    start_date: date | None = Query(None),
    end_date: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: UserInfo = Depends(require_admin),
):
    query = select(SysAuditLog)
    count_query = select(func.count()).select_from(SysAuditLog)

    filters = []
    if username:
        filters.append(SysAuditLog.username == username)
    if action:
        filters.append(SysAuditLog.action == action)
    if start_date:
        filters.append(SysAuditLog.created_at >= datetime.combine(start_date, time.min))
    if end_date:
        # inclusive end-of-day so a single-day [start=end] filter matches that day
        filters.append(SysAuditLog.created_at <= datetime.combine(end_date, time.max))
    for f in filters:
        query = query.where(f)
        count_query = count_query.where(f)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(SysAuditLog.id.desc()).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(query)).scalars().all()

    return PageResult(
        items=[AuditLogOut.model_validate(r) for r in rows],
        total=total,
        page=page,
        page_size=page_size,
    )
