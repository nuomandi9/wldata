"""Integration tests for the Excel import pipeline.

Builds workbooks in-memory with openpyxl, posts them at the preview/commit
endpoints, and asserts on the resulting validation summary + DB rows.
"""
import io
import json

import pytest
from openpyxl import Workbook
from sqlalchemy import select

from models.business import DeliveryRecord


async def get_admin_token(client):
    resp = await client.post(
        "/api/auth/login", json={"username": "admin", "password": "admin123"}
    )
    return resp.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def build_xlsx(headers: list[str], rows: list[list]) -> bytes:
    wb = Workbook()
    ws = wb.active
    ws.append(headers)
    for row in rows:
        ws.append(row)
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


async def seed_dictionaries(client, headers):
    """Create one person, vehicle, route to be referenced by import rows."""
    p = await client.post(
        "/api/dict/person",
        json={"name": "张司机", "id_card": "110101199001011234"},
        headers=headers,
    )
    person_id = p.json()["id"]

    v = await client.post(
        "/api/dict/vehicle",
        json={"plate_number": "京A12345", "driver_id": person_id},
        headers=headers,
    )
    vehicle_id = v.json()["id"]

    r = await client.post(
        "/api/dict/route",
        json={"route_code": "R001", "route_name": "城东一线", "driver_id": person_id},
        headers=headers,
    )
    route_id = r.json()["id"]

    return {"person_id": person_id, "vehicle_id": vehicle_id, "route_id": route_id}


HEADERS = ["日期", "车牌号", "驾驶员", "送货员", "线路编码", "客户数", "送货数", "备注"]


@pytest.mark.asyncio
async def test_list_templates_requires_auth(client, seed_admin):
    resp = await client.get("/api/import/templates")
    assert resp.status_code == 403

    token = await get_admin_token(client)
    resp = await client.get("/api/import/templates", headers=auth_header(token))
    assert resp.status_code == 200
    body = resp.json()
    assert len(body) == 1
    assert body[0]["key"] == "delivery_record"
    assert any(c["header"] == "日期" for c in body[0]["columns"])


@pytest.mark.asyncio
async def test_preview_all_rows_valid(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京A12345", "张司机", None, "R001", 10, 50, "正常"],
        ["2026-05-02", "京A12345", "张司机", "张司机", "R001", 8, 40, ""],
    ])
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("upload.xlsx", xlsx, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 2
    assert body["block_count"] == 0
    assert body["warn_count"] == 0
    assert body["ok_count"] == 2
    assert all(not r["has_block"] and not r["has_warn"] for r in body["rows"])
    # Lookup resolved to FK id
    assert body["rows"][0]["resolved"]["vehicle_id"] is not None


@pytest.mark.asyncio
async def test_preview_block_unknown_vehicle(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京X99999", "张司机", None, "R001", 10, 50, ""],
    ])
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("upload.xlsx", xlsx)},
        headers=headers,
    )
    body = resp.json()
    assert body["block_count"] == 1
    issues = body["rows"][0]["issues"]
    assert any(i["level"] == "BLOCK" and "字典中不存在" in i["message"] for i in issues)


@pytest.mark.asyncio
async def test_preview_block_inactive_vehicle(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    ids = await seed_dictionaries(client, headers)
    # Soft-delete the vehicle so it becomes inactive
    await client.delete(f"/api/dict/vehicle/{ids['vehicle_id']}", headers=headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京A12345", "张司机", None, "R001", 10, 50, ""],
    ])
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("upload.xlsx", xlsx)},
        headers=headers,
    )
    body = resp.json()
    assert body["block_count"] == 1
    issues = body["rows"][0]["issues"]
    assert any(i["level"] == "BLOCK" and "已停用" in i["message"] for i in issues)


@pytest.mark.asyncio
async def test_preview_warn_exceeds_range(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京A12345", "张司机", None, "R001", 250, 600, ""],
    ])
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("upload.xlsx", xlsx)},
        headers=headers,
    )
    body = resp.json()
    assert body["block_count"] == 0
    assert body["warn_count"] == 1
    warn_messages = [i["message"] for i in body["rows"][0]["issues"]]
    assert any("客户数" in m for m in warn_messages)
    assert any("送货数" in m for m in warn_messages)


@pytest.mark.asyncio
async def test_preview_missing_required_header(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    bad_headers = ["车牌号", "驾驶员", "线路编码"]  # missing 日期
    xlsx = build_xlsx(bad_headers, [["京A12345", "张司机", "R001"]])
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("upload.xlsx", xlsx)},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "日期" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_preview_rejects_non_xlsx(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    resp = await client.post(
        "/api/import/delivery_record/preview",
        files={"file": ("bad.csv", b"a,b,c\n1,2,3\n")},
        headers=headers,
    )
    assert resp.status_code == 400
    assert "xlsx" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_commit_inserts_non_block_rows(client, seed_admin, anyio_backend=None):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京A12345", "张司机", None, "R001", 10, 50, "ok1"],
        ["2026-05-02", "京A12345", "张司机", None, "R001", 8, 40, "ok2"],
        ["2026-05-03", "京X99999", "张司机", None, "R001", 5, 30, "block"],  # bad vehicle → BLOCK
    ])

    resp = await client.post(
        "/api/import/delivery_record/commit",
        files={"file": ("upload.xlsx", xlsx)},
        data={
            "commit_row_numbers": json.dumps([1, 2, 3]),
            "warn_notes": json.dumps({}),
        },
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["inserted"] == 2
    assert body["skipped"] == 1
    assert any("BLOCK" in r for r in body["skipped_reasons"])

    # Verify DB state via the existing test_session helper
    from tests.conftest import test_session
    async with test_session() as session:
        result = await session.execute(select(DeliveryRecord))
        rows = result.scalars().all()
        assert len(rows) == 2
        assert {r.remark for r in rows} == {"ok1", "ok2"}
        assert all(r.created_by_user_id is not None for r in rows)


@pytest.mark.asyncio
async def test_commit_warn_requires_notes(client, seed_admin):
    token = await get_admin_token(client)
    headers = auth_header(token)
    await seed_dictionaries(client, headers)

    xlsx = build_xlsx(HEADERS, [
        ["2026-05-01", "京A12345", "张司机", None, "R001", 250, 600, "warn-row"],
    ])

    # Without notes → skipped
    resp = await client.post(
        "/api/import/delivery_record/commit",
        files={"file": ("upload.xlsx", xlsx)},
        data={
            "commit_row_numbers": json.dumps([1]),
            "warn_notes": json.dumps({}),
        },
        headers=headers,
    )
    assert resp.json() == {
        "inserted": 0,
        "skipped": 1,
        "skipped_reasons": ["第 1 行：含 WARN 但未填写备注，已跳过"],
    }

    # With notes → inserted, note persisted
    resp = await client.post(
        "/api/import/delivery_record/commit",
        files={"file": ("upload.xlsx", xlsx)},
        data={
            "commit_row_numbers": json.dumps([1]),
            "warn_notes": json.dumps({"1": "已与司机确认"}),
        },
        headers=headers,
    )
    assert resp.json()["inserted"] == 1

    from tests.conftest import test_session
    async with test_session() as session:
        result = await session.execute(select(DeliveryRecord))
        row = result.scalars().one()
        assert row.warn_notes == "已与司机确认"
