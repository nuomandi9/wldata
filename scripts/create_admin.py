"""Create the initial admin user. Run once after database migration.

Usage: cd backend && python ../scripts/create_admin.py
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))

from sqlalchemy import select
from database import async_session
from models.system import SysUser
from services.auth_service import hash_password


async def main():
    async with async_session() as session:
        result = await session.execute(select(SysUser).where(SysUser.username == "admin"))
        if result.scalar_one_or_none():
            print("Admin user already exists, skipping.")
            return
        user = SysUser(
            username="admin",
            password_hash=hash_password("admin123"),
            real_name="系统管理员",
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.commit()
        print("Admin user created: admin / admin123")


if __name__ == "__main__":
    asyncio.run(main())
