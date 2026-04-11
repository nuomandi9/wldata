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
