from typing import Any, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import select, func, or_, String
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db
from middleware.auth import get_current_user, require_admin
from schemas.auth import UserInfo
from schemas.common import PageResult
from schemas.dict import OptionItem
from services import audit_service


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
    """Build a full CRUD router for one dict domain.

    NOTE: create/update/delete record an audit row (action `dict.create` /
    `dict.update` / `dict.delete`, target_type = table name) in the same
    transaction as the write. If you add new write endpoints here, audit them
    too — auditing lives in the factory so all dict domains stay consistent.
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
            safe = keyword.replace("%", r"\%").replace("_", r"\_")
            conditions = []
            for field_name in search_fields:
                col = getattr(model, field_name)
                conditions.append(col.cast(String).ilike(f"%{safe}%"))
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
        request: Request,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        payload = data.model_dump(exclude_unset=True)
        item = model(**payload)
        db.add(item)
        # flush → audit → commit in one try so a constraint violation at either
        # flush or commit time still surfaces as 409, not 500.
        try:
            await db.flush()            # assigns item.id; raises IntegrityError here on dup
            audit_service.record(
                db, user=admin, action="dict.create",
                target_type=model.__tablename__, target_id=item.id,
                detail={"values": audit_service.scrub(payload)}, request=request,
            )
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="记录已存在（编码或唯一字段重复）")
        await db.refresh(item)
        return out_schema.model_validate(item)

    @router.put("/{item_id}", response_model=out_schema)
    async def update_item(
        item_id: int,
        data: update_schema,
        request: Request,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        changes = data.model_dump(exclude_unset=True)
        before = {k: getattr(item, k) for k in changes}
        for key, value in changes.items():
            setattr(item, key, value)
        try:
            audit_service.record(
                db, user=admin, action="dict.update",
                target_type=model.__tablename__, target_id=item.id,
                detail={"before": audit_service.scrub(before),
                        "after": audit_service.scrub(changes)},
                request=request,
            )
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=409, detail="记录已存在（编码或唯一字段重复）")
        await db.refresh(item)
        return out_schema.model_validate(item)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(
        item_id: int,
        request: Request,
        db: AsyncSession = Depends(get_db),
        admin: UserInfo = Depends(require_admin),
    ):
        result = await db.execute(select(model).where(model.id == item_id))
        item = result.scalar_one_or_none()
        if item is None:
            raise HTTPException(status_code=404, detail="记录不存在")
        item.is_active = False
        audit_service.record(
            db, user=admin, action="dict.delete",
            target_type=model.__tablename__, target_id=item.id,
            detail={}, request=request,
        )
        await db.commit()

    return router
