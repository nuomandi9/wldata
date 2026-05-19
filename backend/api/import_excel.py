"""Excel import API: list templates, preview an uploaded file, commit selected rows.

Stateless design — the same xlsx is uploaded for preview and commit. The
commit step re-validates server-side so dict changes between the two calls
cannot smuggle bad data through. The client tells the server which row
numbers to commit (and supplies warn_notes for WARN rows); BLOCK rows are
never inserted regardless of what the client asks for.
"""
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user
from models.business import DeliveryRecord
from schemas.auth import UserInfo
from schemas.import_excel import (
    CommitResponse, IssueInfo, PreviewResponse, PreviewRow,
    TemplateColumnInfo, TemplateInfo,
)
from services.excel_parser import ExcelParseError, parse_workbook
from services.import_templates import TEMPLATES, get_template
from services.import_validator import BLOCK, WARN, validate_rows


MAX_UPLOAD_BYTES = 50 * 1024 * 1024  # 50 MB per design doc §十

router = APIRouter(prefix="/api/import", tags=["数据导入"])


@router.get("/templates", response_model=list[TemplateInfo])
async def list_templates(current_user: UserInfo = Depends(get_current_user)):
    return [_template_to_info(t) for t in TEMPLATES.values()]


@router.get("/templates/{key}", response_model=TemplateInfo)
async def get_template_detail(
    key: str, current_user: UserInfo = Depends(get_current_user),
):
    tpl = get_template(key)
    if tpl is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    return _template_to_info(tpl)


@router.post("/{key}/preview", response_model=PreviewResponse)
async def preview_upload(
    key: str,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    tpl = get_template(key)
    if tpl is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    file_bytes = await _read_upload(file)

    try:
        raw_rows = parse_workbook(file_bytes, tpl)
    except ExcelParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    validated = await validate_rows(raw_rows, tpl, db)

    block_count = sum(1 for r in validated if r.has_block)
    warn_count = sum(1 for r in validated if r.has_warn and not r.has_block)
    ok_count = len(validated) - block_count - warn_count

    return PreviewResponse(
        template_key=tpl.key,
        total=len(validated),
        block_count=block_count,
        warn_count=warn_count,
        ok_count=ok_count,
        rows=[
            PreviewRow(
                row_number=r.row_number,
                raw=_jsonable(r.raw),
                resolved=_jsonable(r.resolved),
                issues=[IssueInfo(level=i.level, field=i.field, message=i.message)
                        for i in r.issues],
                has_block=r.has_block,
                has_warn=r.has_warn,
            )
            for r in validated
        ],
    )


@router.post("/{key}/commit", response_model=CommitResponse)
async def commit_upload(
    key: str,
    file: UploadFile = File(...),
    commit_row_numbers: str = Form(...),       # JSON-encoded list[int]
    warn_notes: str = Form("{}"),              # JSON-encoded dict[int, str]
    db: AsyncSession = Depends(get_db),
    current_user: UserInfo = Depends(get_current_user),
):
    tpl = get_template(key)
    if tpl is None:
        raise HTTPException(status_code=404, detail="模板不存在")
    try:
        requested_rows = set(json.loads(commit_row_numbers))
        notes_map = {int(k): v for k, v in json.loads(warn_notes).items()}
    except (json.JSONDecodeError, ValueError, TypeError):
        raise HTTPException(status_code=400, detail="commit_row_numbers/warn_notes 格式错误")

    file_bytes = await _read_upload(file)
    try:
        raw_rows = parse_workbook(file_bytes, tpl)
    except ExcelParseError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    validated = await validate_rows(raw_rows, tpl, db)

    inserted = 0
    skipped_reasons: list[str] = []

    for rv in validated:
        if rv.row_number not in requested_rows:
            continue
        if rv.has_block:
            skipped_reasons.append(f"第 {rv.row_number} 行：含 BLOCK 错误，已跳过")
            continue
        if rv.has_warn and rv.row_number not in notes_map:
            skipped_reasons.append(f"第 {rv.row_number} 行：含 WARN 但未填写备注，已跳过")
            continue

        instance = _build_instance(
            tpl, rv.resolved,
            warn_note=notes_map.get(rv.row_number),
            user_id=current_user.user_id,
        )
        db.add(instance)
        inserted += 1

    if inserted:
        await db.commit()

    return CommitResponse(
        inserted=inserted,
        skipped=len(requested_rows) - inserted,
        skipped_reasons=skipped_reasons,
    )


# ── Internals ──

def _template_to_info(tpl) -> TemplateInfo:
    return TemplateInfo(
        key=tpl.key,
        name=tpl.name,
        description=tpl.description,
        columns=[
            TemplateColumnInfo(
                header=c.header, field=c.field, type=c.type, required=c.required,
            ) for c in tpl.columns
        ],
    )


async def _read_upload(file: UploadFile) -> bytes:
    if file.filename and not file.filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="仅支持 xlsx/xls 文件")
    data = await file.read()
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="文件超过 50MB 限制")
    if not data:
        raise HTTPException(status_code=400, detail="文件为空")
    return data


def _build_instance(tpl, resolved: dict, *, warn_note: str | None, user_id: int):
    """Apply only fields the model actually has, plus audit metadata."""
    model = tpl.model
    columns = set(model.__table__.columns.keys())
    payload = {k: v for k, v in resolved.items() if k in columns}
    if warn_note and "warn_notes" in columns:
        payload["warn_notes"] = warn_note
    if "created_by_user_id" in columns:
        payload["created_by_user_id"] = user_id
    return model(**payload)


def _jsonable(d: dict) -> dict:
    """Best-effort JSON-friendly conversion (date → ISO string)."""
    out = {}
    for k, v in d.items():
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out
