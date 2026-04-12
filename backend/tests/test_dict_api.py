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
