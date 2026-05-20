# Step 1: 项目脚手架 + 数据库连接 + 用户认证 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a working foundation — a FastAPI + Vue 3 + PostgreSQL project that supports user login and a basic authenticated layout shell.

**Architecture:** FastAPI backend with SQLAlchemy 2.0 async models, JWT authentication, and a Vue 3 + Element Plus frontend with Vite. PostgreSQL via Docker Compose. Nginx reverse proxy serves the frontend and proxies `/api` to the backend.

**Tech Stack:** Python 3.11+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PyJWT, Vue 3, Element Plus, Vite, Pinia, Vue Router, Docker Compose, PostgreSQL 15

---

## File Structure

```
enterprise-logistics/
├── docker-compose.yml                  # postgres + backend + nginx
├── nginx/
│   └── default.conf                    # proxy /api → backend, serve frontend
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                         # FastAPI app entry, CORS, router mounting
│   ├── config.py                       # Settings via pydantic-settings
│   ├── database.py                     # SQLAlchemy engine, session, Base
│   ├── models/
│   │   └── system.py                   # SysUser model
│   ├── schemas/
│   │   └── auth.py                     # LoginRequest, LoginResponse, UserInfo
│   ├── api/
│   │   └── auth.py                     # POST /login, GET /me
│   ├── services/
│   │   └── auth_service.py             # password hashing, JWT create/verify
│   ├── middleware/
│   │   └── auth.py                     # get_current_user dependency
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/                   # migration scripts
│   └── tests/
│       ├── conftest.py                 # test fixtures (test db, client, auth)
│       ├── test_auth_service.py        # unit tests for auth logic
│       └── test_auth_api.py            # integration tests for auth endpoints
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   └── src/
│       ├── main.js                     # Vue app init + Element Plus + Router + Pinia
│       ├── App.vue                     # Root component with router-view
│       ├── api/
│       │   └── request.js             # Axios instance with JWT interceptor
│       │   └── auth.js                # login(), getMe() API calls
│       ├── stores/
│       │   └── user.js                # Pinia user store (token, userInfo)
│       ├── router/
│       │   └── index.js               # Routes with auth guard
│       ├── views/
│       │   ├── Login.vue              # Login page
│       │   └── Home.vue               # Placeholder home page
│       └── layout/
│           └── MainLayout.vue         # Sidebar + header + content layout shell
└── scripts/
    └── create_admin.py                # CLI script to create initial admin user
```

---

### Task 1: Backend Project Skeleton

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/config.py`
- Create: `backend/database.py`
- Create: `backend/main.py`

- [ ] **Step 1: Create requirements.txt**

```
fastapi==0.115.0
uvicorn[standard]==0.30.0
sqlalchemy[asyncio]==2.0.35
asyncpg==0.29.0
pydantic-settings==2.5.0
pyjwt==2.9.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.9
alembic==1.13.0
openpyxl==3.1.5
pytest==8.3.0
pytest-asyncio==0.24.0
httpx==0.27.0
```

- [ ] **Step 2: Create config.py**

```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tobacco_logistics"
    SECRET_KEY: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 480  # 8 hours

    class Config:
        env_file = ".env"


settings = Settings()
```

- [ ] **Step 3: Create database.py**

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db():
    async with async_session() as session:
        yield session
```

- [ ] **Step 4: Create main.py**

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="“企业”物流数据管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Verify backend starts**

Run: `cd backend && pip install -r requirements.txt && python -m uvicorn main:app --host 0.0.0.0 --port 8000`

Expected: Server starts, `GET http://localhost:8000/api/health` returns `{"status": "ok"}`

- [ ] **Step 6: Commit**

```bash
git add backend/requirements.txt backend/config.py backend/database.py backend/main.py
git commit -m "feat: backend skeleton with FastAPI, config, and database setup"
```

---

### Task 2: User Model + Alembic Migration

**Files:**
- Create: `backend/models/__init__.py`
- Create: `backend/models/system.py`
- Create: `backend/alembic.ini`
- Create: `backend/alembic/env.py`

- [ ] **Step 1: Create models/__init__.py**

```python
from models.system import SysUser

__all__ = ["SysUser"]
```

- [ ] **Step 2: Create models/system.py**

```python
from datetime import datetime

from sqlalchemy import String, Boolean, Integer, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class SysUser(Base):
    __tablename__ = "sys_user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)
    real_name: Mapped[str | None] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(20), nullable=False, default="operator")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
```

- [ ] **Step 3: Initialize Alembic**

Run: `cd backend && alembic init alembic`

- [ ] **Step 4: Configure alembic.ini**

Edit `backend/alembic.ini`, set:
```ini
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/tobacco_logistics
```

- [ ] **Step 5: Configure alembic/env.py for async + model metadata**

Replace `backend/alembic/env.py` with:

```python
import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

from database import Base
import models  # noqa: F401 - ensure all models are imported

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online():
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```

- [ ] **Step 6: Generate initial migration**

Run: `cd backend && alembic revision --autogenerate -m "create sys_user table"`

Expected: A new migration file in `backend/alembic/versions/`

- [ ] **Step 7: Run migration**

Run: `cd backend && alembic upgrade head`

Expected: `sys_user` table created in PostgreSQL

- [ ] **Step 8: Commit**

```bash
git add backend/models/ backend/alembic.ini backend/alembic/
git commit -m "feat: add SysUser model with Alembic async migration"
```

---

### Task 3: Auth Service (password hashing + JWT)

**Files:**
- Create: `backend/services/__init__.py`
- Create: `backend/services/auth_service.py`
- Create: `backend/tests/__init__.py`
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_auth_service.py`

- [ ] **Step 1: Write failing tests for auth service**

Create `backend/tests/__init__.py` (empty file).

Create `backend/tests/conftest.py`:
```python
import pytest
```

Create `backend/tests/test_auth_service.py`:
```python
from services.auth_service import hash_password, verify_password, create_token, decode_token


def test_hash_and_verify_password():
    raw = "mypassword123"
    hashed = hash_password(raw)
    assert hashed != raw
    assert verify_password(raw, hashed) is True
    assert verify_password("wrong", hashed) is False


def test_create_and_decode_token():
    token = create_token(user_id=1, username="admin", role="admin")
    payload = decode_token(token)
    assert payload["user_id"] == 1
    assert payload["username"] == "admin"
    assert payload["role"] == "admin"


def test_decode_invalid_token():
    payload = decode_token("invalid.token.value")
    assert payload is None
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_auth_service.py -v`

Expected: FAIL with `ModuleNotFoundError` or `ImportError`

- [ ] **Step 3: Implement auth service**

Create `backend/services/__init__.py` (empty file).

Create `backend/services/auth_service.py`:
```python
from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int, username: str, role: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": expire,
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except jwt.PyJWTError:
        return None
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_auth_service.py -v`

Expected: 3 passed

- [ ] **Step 5: Commit**

```bash
git add backend/services/ backend/tests/
git commit -m "feat: auth service with password hashing and JWT token management"
```

---

### Task 4: Auth Middleware (get_current_user dependency)

**Files:**
- Create: `backend/middleware/__init__.py`
- Create: `backend/middleware/auth.py`
- Create: `backend/schemas/__init__.py`
- Create: `backend/schemas/auth.py`

- [ ] **Step 1: Create Pydantic schemas**

Create `backend/schemas/__init__.py` (empty file).

Create `backend/schemas/auth.py`:
```python
from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    real_name: str | None = None


class UserInfo(BaseModel):
    user_id: int
    username: str
    role: str
    real_name: str | None = None
```

- [ ] **Step 2: Create auth middleware**

Create `backend/middleware/__init__.py` (empty file).

Create `backend/middleware/auth.py`:
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from services.auth_service import decode_token
from schemas.auth import UserInfo

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> UserInfo:
    payload = decode_token(credentials.credentials)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证令牌",
        )
    return UserInfo(
        user_id=payload["user_id"],
        username=payload["username"],
        role=payload["role"],
    )


async def require_admin(user: UserInfo = Depends(get_current_user)) -> UserInfo:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要管理员权限",
        )
    return user
```

- [ ] **Step 3: Commit**

```bash
git add backend/schemas/ backend/middleware/
git commit -m "feat: auth schemas and JWT middleware with role-based guards"
```

---

### Task 5: Auth API Endpoints + Integration Tests

**Files:**
- Create: `backend/api/__init__.py`
- Create: `backend/api/auth.py`
- Modify: `backend/main.py` (mount router)
- Create: `backend/tests/test_auth_api.py`
- Modify: `backend/tests/conftest.py` (add test DB fixtures)

- [ ] **Step 1: Write failing integration tests**

Update `backend/tests/conftest.py`:
```python
import pytest
import asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from database import Base, get_db
from main import app
from services.auth_service import hash_password
from models.system import SysUser

TEST_DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/tobacco_logistics_test"

test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
test_session = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def override_get_db():
    async with test_session() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.fixture
async def seed_admin():
    async with test_session() as session:
        user = SysUser(
            username="admin",
            password_hash=hash_password("admin123"),
            real_name="管理员",
            role="admin",
            is_active=True,
        )
        session.add(user)
        await session.commit()
```

Create `backend/tests/test_auth_api.py`:
```python
import pytest


@pytest.mark.asyncio
async def test_login_success(client, seed_admin):
    resp = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_login_wrong_password(client, seed_admin):
    resp = await client.post("/api/auth/login", json={"username": "admin", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_nonexistent_user(client):
    resp = await client.post("/api/auth/login", json={"username": "nobody", "password": "any"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_get_me_authenticated(client, seed_admin):
    login_resp = await client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    token = login_resp.json()["access_token"]
    resp = await client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    resp = await client.get("/api/auth/me")
    assert resp.status_code == 403
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd backend && python -m pytest tests/test_auth_api.py -v`

Expected: FAIL (auth router not implemented yet)

- [ ] **Step 3: Implement auth API**

Create `backend/api/__init__.py` (empty file).

Create `backend/api/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from models.system import SysUser
from schemas.auth import LoginRequest, LoginResponse, UserInfo
from services.auth_service import verify_password, create_token
from middleware.auth import get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
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
    return LoginResponse(access_token=token, role=user.role, real_name=user.real_name)


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: UserInfo = Depends(get_current_user)):
    return current_user
```

- [ ] **Step 4: Mount router in main.py**

Replace `backend/main.py` with:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router

app = FastAPI(title="“企业”物流数据管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `cd backend && python -m pytest tests/test_auth_api.py -v`

Expected: 5 passed

- [ ] **Step 6: Commit**

```bash
git add backend/api/ backend/main.py backend/tests/
git commit -m "feat: auth API with login and me endpoints, integration tests"
```

---

### Task 6: Create Admin Script

**Files:**
- Create: `scripts/create_admin.py`

- [ ] **Step 1: Create the script**

```python
"""Create the initial admin user. Run once after database migration.

Usage: cd backend && python ../scripts/create_admin.py
"""
import asyncio
from sqlalchemy import select
from database import engine, async_session
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
```

- [ ] **Step 2: Run the script**

Run: `cd backend && python ../scripts/create_admin.py`

Expected: `Admin user created: admin / admin123`

- [ ] **Step 3: Commit**

```bash
git add scripts/create_admin.py
git commit -m "feat: add create_admin script for initial user setup"
```

---

### Task 7: Frontend Scaffolding

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/vite.config.js`
- Create: `frontend/index.html`
- Create: `frontend/src/main.js`
- Create: `frontend/src/App.vue`

- [ ] **Step 1: Initialize Vue project with Vite**

Run: `cd D:/myleader/wldata && npm create vite@latest frontend -- --template vue`

If the directory already has files, create manually instead.

- [ ] **Step 2: Install dependencies**

Run: `cd frontend && npm install && npm install element-plus @element-plus/icons-vue vue-router@4 pinia axios`

- [ ] **Step 3: Configure vite.config.js**

Replace `frontend/vite.config.js`:
```javascript
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 4: Create src/main.js**

```javascript
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router/index.js'

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(ElementPlus, { locale: zhCn })

for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

app.mount('#app')
```

- [ ] **Step 5: Create src/App.vue**

```vue
<template>
  <router-view />
</template>
```

- [ ] **Step 6: Verify dev server starts**

Run: `cd frontend && npm run dev`

Expected: Vite dev server running at http://localhost:3000

- [ ] **Step 7: Commit**

```bash
git add frontend/
git commit -m "feat: Vue 3 + Element Plus + Vite frontend scaffolding"
```

---

### Task 8: Frontend API Layer + User Store

**Files:**
- Create: `frontend/src/api/request.js`
- Create: `frontend/src/api/auth.js`
- Create: `frontend/src/stores/user.js`

- [ ] **Step 1: Create Axios instance with JWT interceptor**

Create `frontend/src/api/request.js`:
```javascript
import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '../router/index.js'

const request = axios.create({
  baseURL: '',
  timeout: 30000,
})

request.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    if (status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
      ElMessage.error('登录已过期，请重新登录')
    } else if (status === 403) {
      ElMessage.error('没有操作权限')
    } else {
      ElMessage.error(error.response?.data?.detail || '请求失败')
    }
    return Promise.reject(error)
  }
)

export default request
```

- [ ] **Step 2: Create auth API calls**

Create `frontend/src/api/auth.js`:
```javascript
import request from './request.js'

export function login(data) {
  return request.post('/api/auth/login', data)
}

export function getMe() {
  return request.get('/api/auth/me')
}
```

- [ ] **Step 3: Create user store**

Create `frontend/src/stores/user.js`:
```javascript
import { defineStore } from 'pinia'
import { ref } from 'vue'
import { login as loginApi, getMe } from '../api/auth.js'
import router from '../router/index.js'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(null)

  async function login(username, password) {
    const data = await loginApi({ username, password })
    token.value = data.access_token
    localStorage.setItem('token', data.access_token)
    userInfo.value = { username, role: data.role, real_name: data.real_name }
  }

  async function fetchUser() {
    const data = await getMe()
    userInfo.value = data
  }

  function logout() {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    router.push('/login')
  }

  return { token, userInfo, login, fetchUser, logout }
})
```

- [ ] **Step 4: Commit**

```bash
git add frontend/src/api/ frontend/src/stores/
git commit -m "feat: Axios request layer with JWT and Pinia user store"
```

---

### Task 9: Login Page

**Files:**
- Create: `frontend/src/views/Login.vue`

- [ ] **Step 1: Create Login.vue**

```vue
<template>
  <div class="login-container">
    <el-card class="login-card" shadow="hover">
      <template #header>
        <h2 class="login-title">“企业”物流数据管理系统</h2>
      </template>
      <el-form ref="formRef" :model="form" :rules="rules" label-width="0" @submit.prevent="handleLogin">
        <el-form-item prop="username">
          <el-input v-model="form.username" prefix-icon="User" placeholder="用户名" size="large" />
        </el-form-item>
        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            prefix-icon="Lock"
            type="password"
            placeholder="密码"
            size="large"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" size="large" style="width: 100%" :loading="loading" @click="handleLogin">
            登 录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '../stores/user.js'

const router = useRouter()
const userStore = useUserStore()
const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  username: '',
  password: '',
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  loading.value = true
  try {
    await userStore.login(form.username, form.password)
    ElMessage.success('登录成功')
    router.push('/')
  } catch {
    // error handled by interceptor
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-container {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}
.login-card {
  width: 400px;
}
.login-title {
  text-align: center;
  margin: 0;
  font-size: 20px;
  color: #303133;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/views/Login.vue
git commit -m "feat: login page with form validation"
```

---

### Task 10: Main Layout Shell

**Files:**
- Create: `frontend/src/layout/MainLayout.vue`
- Create: `frontend/src/views/Home.vue`

- [ ] **Step 1: Create MainLayout.vue**

```vue
<template>
  <el-container class="layout-container">
    <el-aside :width="isCollapse ? '64px' : '220px'" class="layout-aside">
      <div class="logo">
        <span v-show="!isCollapse">“企业”物流数据管理</span>
        <span v-show="isCollapse">物流</span>
      </div>
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        background-color="#001529"
        text-color="#ffffffa6"
        active-text-color="#ffffff"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <span>首页</span>
        </el-menu-item>
      </el-menu>
    </el-aside>
    <el-container>
      <el-header class="layout-header">
        <el-icon class="collapse-btn" @click="isCollapse = !isCollapse">
          <Fold v-if="!isCollapse" />
          <Expand v-else />
        </el-icon>
        <div class="header-right">
          <span class="user-name">{{ userStore.userInfo?.real_name || userStore.userInfo?.username }}</span>
          <el-button text @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const route = useRoute()
const userStore = useUserStore()
const isCollapse = ref(false)

function handleLogout() {
  userStore.logout()
}
</script>

<style scoped>
.layout-container {
  height: 100vh;
}
.layout-aside {
  background: #001529;
  transition: width 0.3s;
  overflow: hidden;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  white-space: nowrap;
}
.layout-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #ebeef5;
  background: #fff;
}
.collapse-btn {
  font-size: 20px;
  cursor: pointer;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
}
.user-name {
  color: #606266;
}
.layout-main {
  background: #f0f2f5;
}
</style>
```

- [ ] **Step 2: Create Home.vue**

```vue
<template>
  <div>
    <h2>欢迎使用“企业”物流数据管理系统</h2>
    <p>请使用左侧菜单导航。</p>
  </div>
</template>
```

- [ ] **Step 3: Commit**

```bash
git add frontend/src/layout/ frontend/src/views/Home.vue
git commit -m "feat: main layout shell with sidebar navigation and home page"
```

---

### Task 11: Vue Router with Auth Guard

**Files:**
- Create: `frontend/src/router/index.js`

- [ ] **Step 1: Create router with auth guard**

```javascript
import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '../stores/user.js'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/Login.vue'),
    meta: { public: true },
  },
  {
    path: '/',
    component: () => import('../layout/MainLayout.vue'),
    children: [
      {
        path: '',
        name: 'Home',
        component: () => import('../views/Home.vue'),
      },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.public) {
    next()
    return
  }
  if (!token) {
    next('/login')
    return
  }
  const userStore = useUserStore()
  if (!userStore.userInfo) {
    try {
      await userStore.fetchUser()
    } catch {
      next('/login')
      return
    }
  }
  next()
})

export default router
```

- [ ] **Step 2: Verify full flow in browser**

Run backend: `cd backend && uvicorn main:app --reload --port 8000`
Run frontend: `cd frontend && npm run dev`

Test flow:
1. Open http://localhost:3000 → should redirect to /login
2. Enter admin / admin123 → should redirect to / with layout
3. Click "退出" → should return to /login

- [ ] **Step 3: Commit**

```bash
git add frontend/src/router/
git commit -m "feat: Vue Router with auth guard and token-based navigation"
```

---

### Task 12: Docker Compose Setup

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/Dockerfile`
- Create: `frontend/Dockerfile`
- Create: `nginx/default.conf`
- Create: `.env`

- [ ] **Step 1: Create backend/Dockerfile**

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

- [ ] **Step 2: Create frontend/Dockerfile**

```dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
```

- [ ] **Step 3: Create nginx/default.conf**

```nginx
server {
    listen 80;
    server_name localhost;

    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 50m;
    }

    location / {
        root /usr/share/nginx/html;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:15
    restart: always
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: tobacco_logistics
    ports:
      - "5432:5432"
    volumes:
      - pgdata:/var/lib/postgresql/data

  backend:
    build: ./backend
    restart: always
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/tobacco_logistics
      SECRET_KEY: ${SECRET_KEY:-change-me-in-production}
    depends_on:
      - postgres
    ports:
      - "8000:8000"

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "80:80"
    volumes:
      - ./nginx/default.conf:/etc/nginx/conf.d/default.conf
      - frontend_dist:/usr/share/nginx/html
    depends_on:
      - backend

  frontend-build:
    build: ./frontend
    volumes:
      - frontend_dist:/usr/share/nginx/html

volumes:
  pgdata:
  frontend_dist:
```

- [ ] **Step 5: Create .env**

```
SECRET_KEY=your-secret-key-here
```

- [ ] **Step 6: Create .gitignore**

```
# Python
__pycache__/
*.pyc
.env
*.egg-info/
venv/

# Node
node_modules/
frontend/dist/

# IDE
.vscode/
.idea/

# OS
.DS_Store
Thumbs.db
```

- [ ] **Step 7: Verify docker-compose up**

Run: `docker-compose up --build -d`

Expected: All containers start. http://localhost shows the login page.

- [ ] **Step 8: Run migration in container and create admin**

Run:
```bash
docker-compose exec backend alembic upgrade head
docker-compose exec backend python ../scripts/create_admin.py
```

- [ ] **Step 9: Test login through nginx**

Open http://localhost, login with admin/admin123, verify the full flow works.

- [ ] **Step 10: Commit**

```bash
git add docker-compose.yml backend/Dockerfile frontend/Dockerfile nginx/ .env .gitignore
git commit -m "feat: Docker Compose setup with postgres, backend, nginx, and frontend"
```

---

## Summary

After completing all 12 tasks, you will have:
- A running FastAPI + Vue 3 + PostgreSQL system
- JWT-based login authentication
- Role-based middleware (`get_current_user`, `require_admin`)
- Main layout shell with sidebar navigation (ready for menu items)
- Docker Compose for one-command deployment
- Alembic for database migrations
- Test suite for auth service and API
