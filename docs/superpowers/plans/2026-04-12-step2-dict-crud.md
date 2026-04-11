# Step 2: Dictionary CRUD Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a complete dictionary management module with 5 dictionary types (person, vehicle, route, customer, cigarette), using a generic CRUD factory for maximum reuse.

**Architecture:** Backend uses a DictBase mixin + per-dictionary SQLAlchemy models + a CRUD router factory that auto-generates 5 standard endpoints per dictionary. Frontend uses a single config-driven DictTable.vue component that renders any dictionary as a searchable, paginated table with add/edit dialogs.

**Tech Stack:** FastAPI, SQLAlchemy 2.0 (async), Alembic, Pydantic v2, Vue 3, Element Plus, Pinia

---

### Task 1: DictBase Mixin + Person Model

**Files:**
- Create: `backend/models/base.py`
- Create: `backend/models/dict.py`
- Modify: `backend/models/__init__.py`

- [ ] **Step 1: Create DictBase mixin**

Create `backend/models/base.py`:
```python
from datetime import datetime

from sqlalchemy import Integer, Boolean, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class DictBase:
    """Mixin for all dictionary tables."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    extra: Mapped[dict] = mapped_column(JSONB, default=dict, server_default="{}")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
```

- [ ] **Step 2: Create dict_person model**

Create `backend/models/dict.py`:
```python
from sqlalchemy import String, Date, Integer, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from database import Base
from models.base import DictBase


class DictPerson(DictBase, Base):
    __tablename__ = "dict_person"

    name: Mapped[str] = mapped_column(String(50), nullable=False)
    id_card: Mapped[str] = mapped_column(String(18), unique=True, nullable=False)
    birth_date: Mapped[str | None] = mapped_column(Date)
    join_date: Mapped[str | None] = mapped_column(Date)
    position: Mapped[str | None] = mapped_column(String(50))
    department: Mapped[str | None] = mapped_column(String(50))
    employment_type: Mapped[str | None] = mapped_column(String(30))
    school: Mapped[str | None] = mapped_column(String(100))
    degree: Mapped[str | None] = mapped_column(String(30))
```

- [ ] **Step 3: Update models/__init__.py**

Replace `backend/models/__init__.py`:
```python
from models.system import SysUser
from models.dict import DictPerson

__all__ = ["SysUser", "DictPerson"]
```

- [ ] **Step 4: Verify import works**

Run: `cd D:/myleader/wldata/backend && python -c "from models.dict import DictPerson; print(DictPerson.__tablename__)"`

Expected: `dict_person`

- [ ] **Step 5: Commit**

```bash
git add backend/models/base.py backend/models/dict.py backend/models/__init__.py
git commit -m "feat: DictBase mixin and DictPerson model"
```

---

### Task 2: Remaining 4 Dictionary Models

**Files:**
- Modify: `backend/models/dict.py`
- Modify: `backend/models/__init__.py`

- [ ] **Step 1: Add DictVehicle, DictRoute, DictCustomer, DictCigarette to dict.py**

Append to `backend/models/dict.py`:
```python
class DictVehicle(DictBase, Base):
    __tablename__ = "dict_vehicle"

    plate_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    model: Mapped[str | None] = mapped_column(String(50))
    driver_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    cargo_size: Mapped[str | None] = mapped_column(String(30))
    vehicle_type: Mapped[str | None] = mapped_column(String(20))
    tank_or_battery_size: Mapped[float | None] = mapped_column(Numeric(10, 2))
    mileage: Mapped[float | None] = mapped_column(Numeric(12, 2))
    status: Mapped[str | None] = mapped_column(String(20), default="在用")


class DictRoute(DictBase, Base):
    __tablename__ = "dict_route"

    route_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    route_name: Mapped[str] = mapped_column(String(100), nullable=False)
    driver_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    deliverer_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_person.id"))
    customer_count: Mapped[int | None] = mapped_column(Integer)
    delivery_count: Mapped[int | None] = mapped_column(Integer)
    delivery_time: Mapped[str | None] = mapped_column(String(50))
    settlement_time: Mapped[str | None] = mapped_column(String(50))
    response_time_calc: Mapped[str | None] = mapped_column(String(100))
    toll_fee: Mapped[float | None] = mapped_column(Numeric(10, 2))
    delivery_cycle: Mapped[str | None] = mapped_column(String(30))


class DictCustomer(DictBase, Base):
    __tablename__ = "dict_customer"

    customer_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    customer_name: Mapped[str] = mapped_column(String(100), nullable=False)
    address: Mapped[str | None] = mapped_column(String(200))
    phone: Mapped[str | None] = mapped_column(String(20))
    settlement_method: Mapped[str | None] = mapped_column(String(30))
    department: Mapped[str | None] = mapped_column(String(50))
    route_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("dict_route.id"))
    delivery_zone: Mapped[str | None] = mapped_column(String(50))
    delivery_order: Mapped[int | None] = mapped_column(Integer)
    market_type: Mapped[str | None] = mapped_column(String(30))


class DictCigarette(DictBase, Base):
    __tablename__ = "dict_cigarette"

    product_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    brand_owner: Mapped[str | None] = mapped_column(String(100))
    price_category: Mapped[str | None] = mapped_column(String(30))
```

- [ ] **Step 2: Update models/__init__.py**

Replace `backend/models/__init__.py`:
```python
from models.system import SysUser
from models.dict import DictPerson, DictVehicle, DictRoute, DictCustomer, DictCigarette

__all__ = [
    "SysUser",
    "DictPerson",
    "DictVehicle",
    "DictRoute",
    "DictCustomer",
    "DictCigarette",
]
```

- [ ] **Step 3: Verify all imports**

Run: `cd D:/myleader/wldata/backend && python -c "from models import DictPerson, DictVehicle, DictRoute, DictCustomer, DictCigarette; print('OK')"`

Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add backend/models/dict.py backend/models/__init__.py
git commit -m "feat: vehicle, route, customer, cigarette dictionary models"
```

---

### Task 3: Alembic Migration for Dictionary Tables

**Files:**
- Create: `backend/alembic/versions/xxxx_create_dict_tables.py` (auto-generated)

- [ ] **Step 1: Generate migration**

Run: `cd D:/myleader/wldata/backend && alembic revision --autogenerate -m "create dictionary tables"`

- [ ] **Step 2: Review generated migration file**

Open the generated file in `backend/alembic/versions/` and verify it contains:
- `create_table('dict_person', ...)` with all columns including `extra` JSONB
- `create_table('dict_vehicle', ...)` with FK to `dict_person`
- `create_table('dict_route', ...)` with 2 FKs to `dict_person`
- `create_table('dict_customer', ...)` with FK to `dict_route`
- `create_table('dict_cigarette', ...)` standalone
- Proper `downgrade()` with `drop_table` in reverse order

- [ ] **Step 3: Apply migration**

Run: `cd D:/myleader/wldata/backend && alembic upgrade head`

Expected: `INFO  [alembic.runtime.migration] Running upgrade 7c19bf2b8901 -> xxxx, create dictionary tables`

- [ ] **Step 4: Verify tables exist**

Run: `cd D:/myleader/wldata/backend && python -c "
import asyncio
from sqlalchemy import text
from database import engine
async def check():
    async with engine.connect() as conn:
        result = await conn.execute(text(\"SELECT tablename FROM pg_tables WHERE tablename LIKE 'dict_%'\"))
        tables = [r[0] for r in result.fetchall()]
        print(sorted(tables))
asyncio.run(check())
"`

Expected: `['dict_cigarette', 'dict_customer', 'dict_person', 'dict_route', 'dict_vehicle']`

- [ ] **Step 5: Commit**

```bash
git add backend/alembic/versions/
git commit -m "feat: alembic migration for 5 dictionary tables"
```

---

### Task 4: Common Schemas (Pagination)

**Files:**
- Create: `backend/schemas/common.py`

- [ ] **Step 1: Create common pagination schemas**

Create `backend/schemas/common.py`:
```python
from typing import Generic, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    keyword: str | None = None
    is_active: bool | None = None


class PageResult(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
```

- [ ] **Step 2: Verify import**

Run: `cd D:/myleader/wldata/backend && python -c "from schemas.common import PageParams, PageResult; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/schemas/common.py
git commit -m "feat: common pagination schemas"
```

---

### Task 5: Dictionary Schemas

**Files:**
- Create: `backend/schemas/dict.py`

- [ ] **Step 1: Create all dictionary schemas**

Create `backend/schemas/dict.py`:
```python
from datetime import date, datetime
from pydantic import BaseModel


# ── Person ──

class PersonCreate(BaseModel):
    name: str
    id_card: str
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    extra: dict | None = None


class PersonUpdate(BaseModel):
    name: str | None = None
    id_card: str | None = None
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class PersonOut(BaseModel):
    id: int
    name: str
    id_card: str
    birth_date: date | None = None
    join_date: date | None = None
    position: str | None = None
    department: str | None = None
    employment_type: str | None = None
    school: str | None = None
    degree: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Vehicle ──

class VehicleCreate(BaseModel):
    plate_number: str
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = "在用"
    extra: dict | None = None


class VehicleUpdate(BaseModel):
    plate_number: str | None = None
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class VehicleOut(BaseModel):
    id: int
    plate_number: str
    model: str | None = None
    driver_id: int | None = None
    cargo_size: str | None = None
    vehicle_type: str | None = None
    tank_or_battery_size: float | None = None
    mileage: float | None = None
    status: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Route ──

class RouteCreate(BaseModel):
    route_code: str
    route_name: str
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    extra: dict | None = None


class RouteUpdate(BaseModel):
    route_code: str | None = None
    route_name: str | None = None
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class RouteOut(BaseModel):
    id: int
    route_code: str
    route_name: str
    driver_id: int | None = None
    deliverer_id: int | None = None
    customer_count: int | None = None
    delivery_count: int | None = None
    delivery_time: str | None = None
    settlement_time: str | None = None
    response_time_calc: str | None = None
    toll_fee: float | None = None
    delivery_cycle: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Customer ──

class CustomerCreate(BaseModel):
    customer_code: str
    customer_name: str
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    extra: dict | None = None


class CustomerUpdate(BaseModel):
    customer_code: str | None = None
    customer_name: str | None = None
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class CustomerOut(BaseModel):
    id: int
    customer_code: str
    customer_name: str
    address: str | None = None
    phone: str | None = None
    settlement_method: str | None = None
    department: str | None = None
    route_id: int | None = None
    delivery_zone: str | None = None
    delivery_order: int | None = None
    market_type: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Cigarette ──

class CigaretteCreate(BaseModel):
    product_code: str
    product_name: str
    brand_owner: str | None = None
    price_category: str | None = None
    extra: dict | None = None


class CigaretteUpdate(BaseModel):
    product_code: str | None = None
    product_name: str | None = None
    brand_owner: str | None = None
    price_category: str | None = None
    is_active: bool | None = None
    extra: dict | None = None


class CigaretteOut(BaseModel):
    id: int
    product_code: str
    product_name: str
    brand_owner: str | None = None
    price_category: str | None = None
    is_active: bool
    extra: dict | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = {"from_attributes": True}


# ── Options (for foreign key dropdowns) ──

class OptionItem(BaseModel):
    id: int
    label: str

    model_config = {"from_attributes": True}
```

- [ ] **Step 2: Verify import**

Run: `cd D:/myleader/wldata/backend && python -c "from schemas.dict import PersonCreate, PersonOut, VehicleOut, RouteOut, CustomerOut, CigaretteOut, OptionItem; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/schemas/dict.py
git commit -m "feat: Pydantic schemas for 5 dictionary types"
```

---

### Task 6: CRUD Router Factory

**Files:**
- Create: `backend/services/crud_factory.py`

- [ ] **Step 1: Create the generic CRUD factory**

Create `backend/services/crud_factory.py`:
```python
from typing import Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select, func, or_, String
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user, require_admin
from schemas.auth import UserInfo
from schemas.common import PageParams, PageResult
from schemas.dict import OptionItem


def create_crud_router(
    model: Any,
    create_schema: Any,
    update_schema: Any,
    out_schema: Any,
    prefix: str,
    tag: str,
    search_fields: Sequence[str],
    label_field: str = "name",
) -> APIRouter:
    """Generate a standard CRUD router for a dictionary model.

    Args:
        model: SQLAlchemy model class
        create_schema: Pydantic schema for creation
        update_schema: Pydantic schema for update
        out_schema: Pydantic schema for output
        prefix: URL path segment, e.g. "person"
        tag: OpenAPI tag, e.g. "人员管理"
        search_fields: model attribute names to search with keyword
        label_field: field name used as label in /options endpoint
    """
    router = APIRouter(prefix=f"/api/dict/{prefix}", tags=[tag])

    @router.get("", response_model=PageResult[out_schema])
    async def list_items(
        page: int = Query(1, ge=1),
        page_size: int = Query(20, ge=1, le=100),
        keyword: str | None = Query(None),
        is_active: bool | None = Query(None),
        db: AsyncSession = Depends(get_db),
        current_user: UserInfo = Depends(get_current_user),
    ):
        query = select(model)
        count_query = select(func.count()).select_from(model)

        if is_active is not None:
            query = query.where(model.is_active == is_active)
            count_query = count_query.where(model.is_active == is_active)

        if keyword and search_fields:
            conditions = []
            for field_name in search_fields:
                col = getattr(model, field_name)
                conditions.append(col.cast(String).ilike(f"%{keyword}%"))
            query = query.where(or_(*conditions))
            count_query = count_query.where(or_(*conditions))

        total_result = await db.execute(count_query)
        total = total_result.scalar_one()

        query = query.order_by(model.id.desc())
        query = query.offset((page - 1) * page_size).limit(page_size)
        result = await db.execute(query)
        items = result.scalars().all()

        return PageResult(
            items=[out_schema.model_validate(item) for item in items],
            total=total,
            page=page,
            page_size=page_size,
        )

    @router.get("/options", response_model=list[OptionItem])
    async def list_options(
        db: AsyncSession = Depends(get_db),
        current_user: UserInfo = Depends(get_current_user),
    ):
        query = select(model).where(model.is_active == True).order_by(model.id)
        result = await db.execute(query)
        items = result.scalars().all()
        return [
            OptionItem(id=item.id, label=getattr(item, label_field))
            for item in items
        ]

    @router.get("/{item_id}", response_model=out_schema)
    async def get_item(
        item_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserInfo = Depends(get_current_user),
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        return out_schema.model_validate(item)

    @router.post("", response_model=out_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(
        data: create_schema,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        item = model(**data.model_dump(exclude_none=True))
        db.add(item)
        await db.commit()
        await db.refresh(item)
        return out_schema.model_validate(item)

    @router.put("/{item_id}", response_model=out_schema)
    async def update_item(
        item_id: int,
        data: update_schema,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(item, key, value)
        await db.commit()
        await db.refresh(item)
        return out_schema.model_validate(item)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        item_id: int,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        item.is_active = False
        await db.commit()

    return router
```

- [ ] **Step 2: Verify import**

Run: `cd D:/myleader/wldata/backend && python -c "from services.crud_factory import create_crud_router; print('OK')"`

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add backend/services/crud_factory.py
git commit -m "feat: generic CRUD router factory for dictionary management"
```

---

### Task 7: Register Dictionary Routes

**Files:**
- Create: `backend/api/dict.py`
- Modify: `backend/main.py`

- [ ] **Step 1: Create api/dict.py that registers all 5 dictionaries**

Create `backend/api/dict.py`:
```python
from fastapi import APIRouter

from models.dict import DictPerson, DictVehicle, DictRoute, DictCustomer, DictCigarette
from schemas.dict import (
    PersonCreate, PersonUpdate, PersonOut,
    VehicleCreate, VehicleUpdate, VehicleOut,
    RouteCreate, RouteUpdate, RouteOut,
    CustomerCreate, CustomerUpdate, CustomerOut,
    CigaretteCreate, CigaretteUpdate, CigaretteOut,
)
from services.crud_factory import create_crud_router

person_router = create_crud_router(
    model=DictPerson,
    create_schema=PersonCreate,
    update_schema=PersonUpdate,
    out_schema=PersonOut,
    prefix="person",
    tag="人员管理",
    search_fields=["name", "id_card", "department", "position"],
    label_field="name",
)

vehicle_router = create_crud_router(
    model=DictVehicle,
    create_schema=VehicleCreate,
    update_schema=VehicleUpdate,
    out_schema=VehicleOut,
    prefix="vehicle",
    tag="车辆管理",
    search_fields=["plate_number", "model"],
    label_field="plate_number",
)

route_router = create_crud_router(
    model=DictRoute,
    create_schema=RouteCreate,
    update_schema=RouteUpdate,
    out_schema=RouteOut,
    prefix="route",
    tag="线路管理",
    search_fields=["route_code", "route_name"],
    label_field="route_name",
)

customer_router = create_crud_router(
    model=DictCustomer,
    create_schema=CustomerCreate,
    update_schema=CustomerUpdate,
    out_schema=CustomerOut,
    prefix="customer",
    tag="零售客户",
    search_fields=["customer_code", "customer_name", "address"],
    label_field="customer_name",
)

cigarette_router = create_crud_router(
    model=DictCigarette,
    create_schema=CigaretteCreate,
    update_schema=CigaretteUpdate,
    out_schema=CigaretteOut,
    prefix="cigarette",
    tag="卷烟品牌",
    search_fields=["product_code", "product_name", "brand_owner"],
    label_field="product_name",
)

# Aggregate router for easy inclusion
router = APIRouter()
router.include_router(person_router)
router.include_router(vehicle_router)
router.include_router(route_router)
router.include_router(customer_router)
router.include_router(cigarette_router)
```

- [ ] **Step 2: Update main.py to include dict router**

Replace `backend/main.py`:
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.auth import router as auth_router
from api.dict import router as dict_router

app = FastAPI(title="烟草物流数据管理系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(dict_router)


@app.get("/api/health")
async def health():
    return {"status": "ok"}
```

- [ ] **Step 3: Verify API docs load**

Run: `cd D:/myleader/wldata/backend && python -c "from main import app; print([r.path for r in app.routes if '/dict/' in getattr(r, 'path', '')])"`

Expected: List of paths including `/api/dict/person`, `/api/dict/vehicle`, etc.

- [ ] **Step 4: Commit**

```bash
git add backend/api/dict.py backend/main.py
git commit -m "feat: register 5 dictionary CRUD routes in FastAPI"
```

---

### Task 8: Backend Integration Tests

**Files:**
- Create: `backend/tests/test_dict_api.py`

- [ ] **Step 1: Create dict API tests**

Create `backend/tests/test_dict_api.py`:
```python
import pytest


async def get_admin_token(client):
    resp = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_person_crud_full_cycle(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)

    # Create
    resp = await client.post(
        "/api/dict/person",
        json={"name": "张三", "id_card": "110101199001011234"},
        headers=headers,
    )
    assert resp.status_code == 201
    person = resp.json()
    person_id = person["id"]
    assert person["name"] == "张三"
    assert person["is_active"] is True

    # List
    resp = await client.get("/api/dict/person", headers=headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(p["id"] == person_id for p in data["items"])

    # Search by keyword
    resp = await client.get("/api/dict/person?keyword=张", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["total"] >= 1

    # Get by id
    resp = await client.get(f"/api/dict/person/{person_id}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["name"] == "张三"

    # Update
    resp = await client.put(
        f"/api/dict/person/{person_id}",
        json={"department": "配送部"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["department"] == "配送部"

    # Soft delete
    resp = await client.delete(f"/api/dict/person/{person_id}", headers=headers)
    assert resp.status_code == 204

    # Verify soft deleted
    resp = await client.get(f"/api/dict/person/{person_id}", headers=headers)
    assert resp.json()["is_active"] is False

    # Options returns only active
    resp = await client.get("/api/dict/person/options", headers=headers)
    assert resp.status_code == 200
    assert all(item["id"] != person_id for item in resp.json())


@pytest.mark.asyncio
async def test_vehicle_with_foreign_key(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)

    # Create person first (driver)
    resp = await client.post(
        "/api/dict/person",
        json={"name": "李四", "id_card": "110101199002021234"},
        headers=headers,
    )
    driver_id = resp.json()["id"]

    # Create vehicle with driver FK
    resp = await client.post(
        "/api/dict/vehicle",
        json={
            "plate_number": "京A12345",
            "vehicle_type": "新能源",
            "driver_id": driver_id,
        },
        headers=headers,
    )
    assert resp.status_code == 201
    assert resp.json()["driver_id"] == driver_id


@pytest.mark.asyncio
async def test_dict_requires_admin(client, seed_admin):
    # Create an operator user
    token = await get_admin_token(client)
    headers = auth_header(token)

    # Operator can list (via get_current_user)
    resp = await client.get("/api/dict/person", headers=headers)
    assert resp.status_code == 200

    # No token should fail
    resp = await client.post(
        "/api/dict/person",
        json={"name": "Test", "id_card": "000000000000000000"},
    )
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_not_found(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    resp = await client.get("/api/dict/person/99999", headers=headers)
    assert resp.status_code == 404
```

- [ ] **Step 2: Run tests**

Run: `cd D:/myleader/wldata/backend && python -m pytest tests/test_dict_api.py -v`

Expected: All tests PASS

- [ ] **Step 3: Run full test suite to check for regressions**

Run: `cd D:/myleader/wldata/backend && python -m pytest -v`

Expected: All tests PASS (auth + dict)

- [ ] **Step 4: Commit**

```bash
git add backend/tests/test_dict_api.py
git commit -m "test: dictionary CRUD API integration tests"
```

---

### Task 9: Frontend Dictionary Config Files

**Files:**
- Create: `frontend/src/dict-config/person.js`
- Create: `frontend/src/dict-config/vehicle.js`
- Create: `frontend/src/dict-config/route.js`
- Create: `frontend/src/dict-config/customer.js`
- Create: `frontend/src/dict-config/cigarette.js`

- [ ] **Step 1: Create person config**

Create `frontend/src/dict-config/person.js`:
```javascript
export default {
  api: '/api/dict/person',
  title: '人员管理',
  columns: [
    { prop: 'name', label: '姓名', required: true, searchable: true, width: 100 },
    { prop: 'id_card', label: '身份证号', required: true, width: 180 },
    { prop: 'department', label: '部门', searchable: true, width: 100 },
    { prop: 'position', label: '岗位', searchable: true, width: 100 },
    { prop: 'employment_type', label: '用工类型', width: 100 },
    { prop: 'birth_date', label: '出生年月', type: 'date', width: 120 },
    { prop: 'join_date', label: '进入单位时间', type: 'date', width: 120 },
    { prop: 'school', label: '毕业院校', width: 140 },
    { prop: 'degree', label: '学位', width: 80 },
  ],
}
```

- [ ] **Step 2: Create vehicle config**

Create `frontend/src/dict-config/vehicle.js`:
```javascript
export default {
  api: '/api/dict/vehicle',
  title: '车辆管理',
  columns: [
    { prop: 'plate_number', label: '车牌号', required: true, searchable: true, width: 120 },
    { prop: 'model', label: '车型', searchable: true, width: 100 },
    { prop: 'driver_id', label: '驾驶员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'vehicle_type', label: '车辆类型', width: 100,
      type: 'enum', choices: ['油车', '新能源'] },
    { prop: 'cargo_size', label: '车厢大小', width: 100 },
    { prop: 'tank_or_battery_size', label: '油箱/电池容量', type: 'number', width: 130 },
    { prop: 'mileage', label: '行驶里程(km)', type: 'number', width: 120 },
    { prop: 'status', label: '状态', width: 80,
      type: 'enum', choices: ['在用', '停用', '维修'] },
  ],
}
```

- [ ] **Step 3: Create route config**

Create `frontend/src/dict-config/route.js`:
```javascript
export default {
  api: '/api/dict/route',
  title: '线路管理',
  columns: [
    { prop: 'route_code', label: '线路编码', required: true, searchable: true, width: 120 },
    { prop: 'route_name', label: '线路名称', required: true, searchable: true, width: 140 },
    { prop: 'driver_id', label: '驾驶员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'deliverer_id', label: '送货员', type: 'select', width: 100,
      options: { api: '/api/dict/person/options' } },
    { prop: 'customer_count', label: '客户数量', type: 'number', width: 100 },
    { prop: 'delivery_count', label: '送货数量', type: 'number', width: 100 },
    { prop: 'delivery_time', label: '送货时间', width: 100 },
    { prop: 'settlement_time', label: '结算时间', width: 100 },
    { prop: 'response_time_calc', label: '响应时间计算', width: 130 },
    { prop: 'toll_fee', label: '过路费', type: 'number', width: 100 },
    { prop: 'delivery_cycle', label: '送货周期', width: 100 },
  ],
}
```

- [ ] **Step 4: Create customer config**

Create `frontend/src/dict-config/customer.js`:
```javascript
export default {
  api: '/api/dict/customer',
  title: '零售客户',
  columns: [
    { prop: 'customer_code', label: '客户编码', required: true, searchable: true, width: 120 },
    { prop: 'customer_name', label: '客户名称', required: true, searchable: true, width: 140 },
    { prop: 'address', label: '客户地址', searchable: true, width: 200 },
    { prop: 'phone', label: '电话', width: 120 },
    { prop: 'settlement_method', label: '结算方式', width: 100 },
    { prop: 'department', label: '所属部门', width: 100 },
    { prop: 'route_id', label: '配送线路', type: 'select', width: 120,
      options: { api: '/api/dict/route/options' } },
    { prop: 'delivery_zone', label: '配送域', width: 100 },
    { prop: 'delivery_order', label: '送货顺序', type: 'number', width: 100 },
    { prop: 'market_type', label: '市场类型', width: 100 },
  ],
}
```

- [ ] **Step 5: Create cigarette config**

Create `frontend/src/dict-config/cigarette.js`:
```javascript
export default {
  api: '/api/dict/cigarette',
  title: '卷烟品牌',
  columns: [
    { prop: 'product_code', label: '商品编码', required: true, searchable: true, width: 120 },
    { prop: 'product_name', label: '商品名称', required: true, searchable: true, width: 140 },
    { prop: 'brand_owner', label: '品牌拥有者', searchable: true, width: 140 },
    { prop: 'price_category', label: '价类', width: 100 },
  ],
}
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/dict-config/
git commit -m "feat: dictionary config files for 5 dictionary types"
```

---

### Task 10: DictTable.vue Generic Component

**Files:**
- Create: `frontend/src/components/DictTable.vue`

- [ ] **Step 1: Create the generic DictTable component**

Create `frontend/src/components/DictTable.vue`:
```vue
<template>
  <div class="dict-page">
    <!-- Header bar -->
    <div class="dict-header">
      <h2 class="dict-title">{{ config.title }}</h2>
      <div class="dict-actions">
        <el-input
          v-model="keyword"
          placeholder="搜索..."
          clearable
          class="search-input"
          @input="debouncedSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" class="add-btn" @click="openDialog(null)">
          <el-icon><Plus /></el-icon>新增
        </el-button>
      </div>
    </div>

    <!-- Table -->
    <div class="dict-table-card">
      <el-table
        :data="tableData"
        v-loading="loading"
        stripe
        class="dict-table"
        @sort-change="handleSortChange"
      >
        <el-table-column type="index" label="#" width="50" />
        <el-table-column
          v-for="col in config.columns"
          :key="col.prop"
          :prop="col.prop"
          :label="col.label"
          :width="col.width"
          :sortable="col.sortable ? 'custom' : false"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <!-- Select (FK) display label -->
            <span v-if="col.type === 'select'">
              {{ getOptionLabel(col.prop, row[col.prop]) }}
            </span>
            <!-- Status tag -->
            <el-tag
              v-else-if="col.prop === 'is_active'"
              :type="row.is_active ? 'success' : 'danger'"
              size="small"
            >
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
            <!-- Default -->
            <span v-else>{{ row[col.prop] ?? '-' }}</span>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="80">
          <template #default="{ row }">
            <el-tag :type="row.is_active ? 'success' : 'danger'" size="small">
              {{ row.is_active ? '启用' : '停用' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="openDialog(row)">编辑</el-button>
            <el-popconfirm
              title="确认停用该记录？"
              confirm-button-text="确认"
              cancel-button-text="取消"
              @confirm="handleDelete(row)"
            >
              <template #reference>
                <el-button link type="danger" size="small" :disabled="!row.is_active">停用</el-button>
              </template>
            </el-popconfirm>
          </template>
        </el-table-column>
      </el-table>

      <!-- Pagination -->
      <div class="dict-pagination">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[20, 50, 100]"
          layout="total, sizes, prev, pager, next"
          @current-change="fetchData"
          @size-change="fetchData"
        />
      </div>
    </div>

    <!-- Add / Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEdit ? '编辑' : '新增'"
      width="600px"
      destroy-on-close
      class="dict-dialog"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="110px">
        <el-form-item
          v-for="col in config.columns"
          :key="col.prop"
          :label="col.label"
          :prop="col.prop"
        >
          <!-- Date -->
          <el-date-picker
            v-if="col.type === 'date'"
            v-model="formData[col.prop]"
            type="date"
            value-format="YYYY-MM-DD"
            placeholder="选择日期"
            style="width: 100%"
          />
          <!-- Number -->
          <el-input-number
            v-else-if="col.type === 'number'"
            v-model="formData[col.prop]"
            :controls="false"
            style="width: 100%"
          />
          <!-- Enum dropdown -->
          <el-select
            v-else-if="col.type === 'enum'"
            v-model="formData[col.prop]"
            placeholder="请选择"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="c in col.choices"
              :key="c"
              :label="c"
              :value="c"
            />
          </el-select>
          <!-- FK select -->
          <el-select
            v-else-if="col.type === 'select'"
            v-model="formData[col.prop]"
            placeholder="请选择"
            clearable
            filterable
            style="width: 100%"
          >
            <el-option
              v-for="opt in optionsMap[col.prop]"
              :key="opt.id"
              :label="opt.label"
              :value="opt.id"
            />
          </el-select>
          <!-- Default text input -->
          <el-input v-else v-model="formData[col.prop]" clearable />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import request from '../api/request.js'

const props = defineProps({
  config: { type: Object, required: true },
})

// ── State ──
const tableData = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)
const keyword = ref('')

const dialogVisible = ref(false)
const isEdit = ref(false)
const editingId = ref(null)
const formRef = ref(null)
const formData = reactive({})
const submitting = ref(false)

// FK options cache: { driver_id: [{id, label}], ... }
const optionsMap = reactive({})

// ── Computed ──
const formRules = computed(() => {
  const rules = {}
  for (const col of props.config.columns) {
    if (col.required) {
      rules[col.prop] = [{ required: true, message: `请输入${col.label}`, trigger: 'blur' }]
    }
  }
  return rules
})

// ── Debounce search ──
let searchTimer = null
function debouncedSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    fetchData()
  }, 300)
}

// ── Fetch data ──
async function fetchData() {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (keyword.value) params.keyword = keyword.value
    const data = await request.get(props.config.api, { params })
    tableData.value = data.items
    total.value = data.total
  } finally {
    loading.value = false
  }
}

// ── Fetch FK options ──
async function fetchOptions() {
  for (const col of props.config.columns) {
    if (col.type === 'select' && col.options?.api) {
      try {
        const data = await request.get(col.options.api)
        optionsMap[col.prop] = data
      } catch {
        optionsMap[col.prop] = []
      }
    }
  }
}

function getOptionLabel(prop, value) {
  if (value == null) return '-'
  const list = optionsMap[prop] || []
  const item = list.find((o) => o.id === value)
  return item ? item.label : value
}

// ── Dialog ──
function openDialog(row) {
  isEdit.value = !!row
  editingId.value = row?.id || null
  // Reset form
  for (const col of props.config.columns) {
    formData[col.prop] = row ? row[col.prop] : (col.type === 'number' ? null : '')
  }
  dialogVisible.value = true
}

async function handleSubmit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {}
    for (const col of props.config.columns) {
      const val = formData[col.prop]
      if (val !== '' && val !== null && val !== undefined) {
        payload[col.prop] = val
      }
    }
    if (isEdit.value) {
      await request.put(`${props.config.api}/${editingId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await request.post(props.config.api, payload)
      ElMessage.success('新增成功')
    }
    dialogVisible.value = false
    fetchData()
  } finally {
    submitting.value = false
  }
}

// ── Delete (soft) ──
async function handleDelete(row) {
  await request.delete(`${props.config.api}/${row.id}`)
  ElMessage.success('已停用')
  fetchData()
}

// ── Sort (placeholder for future) ──
function handleSortChange() {
  // future: pass sort params to API
}

// ── Init ──
onMounted(() => {
  fetchData()
  fetchOptions()
})
</script>

<style scoped>
.dict-page {
  font-family: 'DM Sans', 'Noto Serif SC', sans-serif;
}

.dict-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 20px;
}

.dict-title {
  font-family: 'Noto Serif SC', serif;
  font-size: 20px;
  font-weight: 600;
  color: #0a1628;
  margin: 0;
}

.dict-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.search-input {
  width: 240px;
}

.search-input :deep(.el-input__wrapper) {
  border-radius: 8px;
}

.add-btn {
  background: linear-gradient(135deg, #0a1628, #162847);
  border: none;
  border-radius: 8px;
  font-weight: 500;
}

.add-btn:hover {
  background: linear-gradient(135deg, #c8956c, #e8b888);
  color: #0a1628;
}

.dict-table-card {
  background: #fff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid rgba(10, 22, 40, 0.05);
}

.dict-table {
  width: 100%;
}

.dict-table :deep(.el-table__header th) {
  background: #faf8f5 !important;
  color: #0a1628;
  font-weight: 600;
  font-size: 13px;
}

.dict-table :deep(.el-table__row) {
  font-size: 13px;
}

.dict-pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}

.dict-dialog :deep(.el-dialog__header) {
  background: linear-gradient(135deg, #0a1628, #162847);
  margin: 0;
  padding: 16px 20px;
}

.dict-dialog :deep(.el-dialog__title) {
  color: #f5f0eb;
  font-family: 'Noto Serif SC', serif;
}

.dict-dialog :deep(.el-dialog__headerbtn .el-dialog__close) {
  color: #8a9bb5;
}

.dict-dialog :deep(.el-dialog__body) {
  padding: 24px 20px;
}
</style>
```

- [ ] **Step 2: Commit**

```bash
git add frontend/src/components/DictTable.vue
git commit -m "feat: generic DictTable component with search, pagination, CRUD dialog"
```

---

### Task 11: Dictionary View Pages

**Files:**
- Create: `frontend/src/views/dict/Person.vue`
- Create: `frontend/src/views/dict/Vehicle.vue`
- Create: `frontend/src/views/dict/Route.vue`
- Create: `frontend/src/views/dict/Customer.vue`
- Create: `frontend/src/views/dict/Cigarette.vue`

- [ ] **Step 1: Create Person.vue**

Create `frontend/src/views/dict/Person.vue`:
```vue
<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/person.js'
</script>
```

- [ ] **Step 2: Create Vehicle.vue**

Create `frontend/src/views/dict/Vehicle.vue`:
```vue
<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/vehicle.js'
</script>
```

- [ ] **Step 3: Create Route.vue**

Create `frontend/src/views/dict/Route.vue`:
```vue
<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/route.js'
</script>
```

- [ ] **Step 4: Create Customer.vue**

Create `frontend/src/views/dict/Customer.vue`:
```vue
<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/customer.js'
</script>
```

- [ ] **Step 5: Create Cigarette.vue**

Create `frontend/src/views/dict/Cigarette.vue`:
```vue
<template>
  <DictTable :config="config" />
</template>

<script setup>
import DictTable from '../../components/DictTable.vue'
import config from '../../dict-config/cigarette.js'
</script>
```

- [ ] **Step 6: Commit**

```bash
git add frontend/src/views/dict/
git commit -m "feat: 5 dictionary view pages using DictTable component"
```

---

### Task 12: Router + Sidebar Menu

**Files:**
- Modify: `frontend/src/router/index.js`
- Modify: `frontend/src/layout/MainLayout.vue`

- [ ] **Step 1: Add dictionary routes to router/index.js**

Replace `frontend/src/router/index.js`:
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
      {
        path: 'dict/person',
        name: 'DictPerson',
        component: () => import('../views/dict/Person.vue'),
      },
      {
        path: 'dict/vehicle',
        name: 'DictVehicle',
        component: () => import('../views/dict/Vehicle.vue'),
      },
      {
        path: 'dict/route',
        name: 'DictRoute',
        component: () => import('../views/dict/Route.vue'),
      },
      {
        path: 'dict/customer',
        name: 'DictCustomer',
        component: () => import('../views/dict/Customer.vue'),
      },
      {
        path: 'dict/cigarette',
        name: 'DictCigarette',
        component: () => import('../views/dict/Cigarette.vue'),
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

- [ ] **Step 2: Update MainLayout.vue sidebar menu**

In `frontend/src/layout/MainLayout.vue`, replace the `<el-menu>` block (inside `<el-aside>`) with:

```vue
      <el-menu
        :default-active="route.path"
        :collapse="isCollapse"
        router
        class="side-menu"
      >
        <el-menu-item index="/">
          <el-icon><HomeFilled /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        <el-sub-menu index="dict">
          <template #title>
            <el-icon><Folder /></el-icon>
            <span>字典管理</span>
          </template>
          <el-menu-item index="/dict/person">
            <el-icon><User /></el-icon>
            <template #title>人员管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/vehicle">
            <el-icon><Van /></el-icon>
            <template #title>车辆管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/route">
            <el-icon><Guide /></el-icon>
            <template #title>线路管理</template>
          </el-menu-item>
          <el-menu-item index="/dict/customer">
            <el-icon><OfficeBuilding /></el-icon>
            <template #title>零售客户</template>
          </el-menu-item>
          <el-menu-item index="/dict/cigarette">
            <el-icon><Goods /></el-icon>
            <template #title>卷烟品牌</template>
          </el-menu-item>
        </el-sub-menu>
      </el-menu>
```

- [ ] **Step 3: Verify frontend builds**

Run: `cd D:/myleader/wldata/frontend && npx vite build --mode development 2>&1 | tail -5`

Expected: `✓ built in ...` with no errors

- [ ] **Step 4: Commit**

```bash
git add frontend/src/router/index.js frontend/src/layout/MainLayout.vue
git commit -m "feat: dictionary routes and sidebar sub-menu"
```

---

### Task 13: End-to-End Verification

**Files:** None (verification only)

- [ ] **Step 1: Start backend**

Run: `cd D:/myleader/wldata/backend && source venv/Scripts/activate && uvicorn main:app --reload --port 8000`

- [ ] **Step 2: Start frontend**

Run: `cd D:/myleader/wldata/frontend && npm run dev`

- [ ] **Step 3: Verify API docs**

Open http://localhost:8000/docs — verify all `/api/dict/*` endpoints appear with correct tags.

- [ ] **Step 4: Test in browser**

Open http://localhost:3000:
1. Login with admin/admin123
2. Sidebar shows "字典管理" with 5 sub-items
3. Click "人员管理" → empty table loads with search + pagination
4. Click "新增" → form dialog opens with all fields
5. Fill in name=测试员 id_card=110101199001011234 → submit → row appears in table
6. Click "编辑" → form pre-filled → change department → submit → updated
7. Click "停用" → confirm → status changes to red "停用" tag
8. Type keyword in search → table filters
9. Navigate to "车辆管理" → "驾驶员" field shows dropdown with the person just created
10. Navigate to "线路管理" → "驾驶员" and "送货员" dropdowns work
11. Navigate to "零售客户" → "配送线路" dropdown shows routes
12. Navigate to "卷烟品牌" → simple form with 4 fields works

- [ ] **Step 5: Run full test suite one final time**

Run: `cd D:/myleader/wldata/backend && python -m pytest -v`

Expected: All tests PASS
