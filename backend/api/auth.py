from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.system import SysUser
from schemas.auth import LoginRequest, LoginResponse, UserInfo
from services.auth_service import verify_password, create_token
from services import audit_service
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, request: Request, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(SysUser).where(SysUser.username == req.username))
    user = result.scalar_one_or_none()
    if user is None or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="账号已停用",
        )
    token = create_token(user_id=user.id, username=user.username, role=user.role)
    # "login" audits *successful* logins only. Login is otherwise read-only,
    # so we commit the audit row ourselves.
    audit_service.record(
        db,
        user=UserInfo(user_id=user.id, username=user.username, role=user.role),
        action="login",
        request=request,
    )
    await db.commit()
    return LoginResponse(access_token=token, role=user.role, real_name=user.real_name)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    return current_user
