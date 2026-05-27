"""User management — admin only.

No hard delete: users are disabled via `is_active=False`. Two safety guards:
  - an admin cannot demote or disable *themselves* (foot-gun / lock-out),
  - the *last active admin* cannot be demoted or disabled (system lock-out).

All writes are audited with a scrubbed detail dict — passwords never reach the
audit log.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import require_admin
from models.system import SysUser
from schemas.auth import UserInfo
from schemas.common import PageResult
from schemas.user import PasswordReset, UserCreate, UserOut, UserUpdate
from services.auth_service import hash_password
from services import audit_service

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("", response_model=PageResult[UserOut])
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    admin: UserInfo = Depends(require_admin),
):
    query = select(SysUser)
    count_query = select(func.count()).select_from(SysUser)
    if keyword:
        safe = keyword.replace("%", r"\%").replace("_", r"\_")
        cond = SysUser.username.ilike(f"%{safe}%") | SysUser.real_name.ilike(f"%{safe}%")
        query = query.where(cond)
        count_query = count_query.where(cond)

    total = (await db.execute(count_query)).scalar_one()
    query = query.order_by(SysUser.id).offset((page - 1) * page_size).limit(page_size)
    rows = (await db.execute(query)).scalars().all()
    return PageResult(
        items=[UserOut.model_validate(r) for r in rows],
        total=total, page=page, page_size=page_size,
    )


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: UserInfo = Depends(require_admin),
):
    user = SysUser(
        username=data.username,
        password_hash=hash_password(data.password),
        real_name=data.real_name,
        role=data.role,
        is_active=True,
    )
    db.add(user)
    try:
        await db.flush()
        audit_service.record(
            db, user=admin, action="user.create",
            target_type="sys_user", target_id=user.id,
            detail={"username": user.username, "role": user.role},  # never the password
            request=request,
        )
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="用户名已存在")
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.put("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: int,
    data: UserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: UserInfo = Depends(require_admin),
):
    user = (await db.execute(select(SysUser).where(SysUser.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")

    changes = data.model_dump(exclude_unset=True)
    demoting = changes.get("role") not in (None, "admin") and user.role == "admin"
    disabling = changes.get("is_active") is False and user.is_active

    if (demoting or disabling) and user.id == admin.user_id:
        raise HTTPException(status_code=400, detail="不能停用或降级自己的账号")
    if (demoting or disabling) and await _is_last_active_admin(db, user):
        raise HTTPException(status_code=400, detail="系统必须保留至少一个在用管理员")

    before = {k: getattr(user, k) for k in changes}
    for key, value in changes.items():
        setattr(user, key, value)

    audit_service.record(
        db, user=admin, action="user.update",
        target_type="sys_user", target_id=user.id,
        detail={"before": audit_service.scrub(before), "after": audit_service.scrub(changes)},
        request=request,
    )
    await db.commit()
    await db.refresh(user)
    return UserOut.model_validate(user)


@router.post("/{user_id}/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    user_id: int,
    data: PasswordReset,
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: UserInfo = Depends(require_admin),
):
    user = (await db.execute(select(SysUser).where(SysUser.id == user_id))).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.password_hash = hash_password(data.new_password)
    audit_service.record(
        db, user=admin, action="user.reset_password",
        target_type="sys_user", target_id=user.id,
        detail={"username": user.username},  # never the new password
        request=request,
    )
    await db.commit()


async def _is_last_active_admin(db: AsyncSession, user: SysUser) -> bool:
    """True if `user` is the only remaining active admin."""
    if user.role != "admin" or not user.is_active:
        return False
    others = (await db.execute(
        select(func.count()).select_from(SysUser).where(
            SysUser.role == "admin",
            SysUser.is_active.is_(True),
            SysUser.id != user.id,
        )
    )).scalar_one()
    return others == 0
