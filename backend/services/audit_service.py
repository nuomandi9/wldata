"""Operation audit trail.

`record()` adds a `SysAuditLog` row to the **caller's** session and does NOT
commit — so the audited operation and its audit row commit (or roll back)
atomically in one transaction. The only exception is read-only endpoints
(e.g. login) that otherwise issue no writes; those call `record()` and then
commit themselves.

SECURITY: `detail` is always a pre-built dict supplied by the call site. Never
pass a raw request body — that is how plaintext passwords leak into the log.
Each call site is responsible for scrubbing secrets before handing over detail.

`detail` shape per action (keep this list authoritative):
  - "login"               → {}                       (username + ip on the row)
  - "dict.create"         → {"values": {...}}         scrubbed snapshot of new row
  - "dict.update"         → {"before": {...}, "after": {...}}   changed fields only
  - "dict.delete"         → {}                        (target_id carries the row)
  - "import.commit_warn"  → {"template": key, "inserted": n,
                             "forced_rows": [{"row_number": int, "warn_note": str}]}
  - "user.create"         → {"username": str, "role": str}       NEVER password
  - "user.update"         → {"before": {...}, "after": {...}}     role/is_active/real_name only
  - "user.reset_password" → {"username": str}                    NEVER the new password
"""
from datetime import date, datetime
from typing import Any

from fastapi import Request

from models.system import SysAuditLog
from schemas.auth import UserInfo


def client_ip(request: Request | None) -> str | None:
    """Best-effort client IP. Behind nginx the real client is the first hop of
    X-Forwarded-For; fall back to the direct peer."""
    if request is None:
        return None
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else None


_SECRET_FRAGMENTS = ("password", "passwd", "pwd", "secret", "token")


def scrub(values: dict[str, Any]) -> dict[str, Any]:
    """Make a JSONB-safe, secret-free snapshot: drop secret-ish keys and
    ISO-stringify dates/datetimes (asyncpg JSONB has no native date codec).

    This is a defense-in-depth net; call sites must still avoid handing raw
    request bodies to the audit log in the first place."""
    out: dict[str, Any] = {}
    for k, v in values.items():
        key_l = k.lower()
        if any(frag in key_l for frag in _SECRET_FRAGMENTS):
            continue
        if isinstance(v, (date, datetime)):
            out[k] = v.isoformat()
        else:
            out[k] = v
    return out


def record(
    db,
    *,
    user: UserInfo | None,
    action: str,
    target_type: str | None = None,
    target_id: Any | None = None,
    detail: dict | None = None,
    request: Request | None = None,
) -> SysAuditLog:
    """Stage one audit row in the caller's session. Caller commits."""
    entry = SysAuditLog(
        user_id=user.user_id if user else None,
        username=user.username if user else None,
        action=action,
        target_type=target_type,
        target_id=str(target_id) if target_id is not None else None,
        detail=detail or {},
        ip=client_ip(request),
    )
    db.add(entry)
    return entry
