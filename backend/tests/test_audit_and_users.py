"""Integration tests for audit logging + user management (Step 5)."""
import json

import pytest


async def get_token(client, username="admin", password="admin123"):
    resp = await client.post(
        "/api/auth/login", json={"username": username, "password": password}
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


# ── Audit logging ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_writes_audit_row(client, seed_admin):
    token = await get_token(client)
    resp = await client.get("/api/audit/logs", headers=auth(token))
    assert resp.status_code == 200
    actions = [r["action"] for r in resp.json()["items"]]
    assert "login" in actions


@pytest.mark.asyncio
async def test_dict_create_writes_audit_row(client, seed_admin):
    token = await get_token(client)
    await client.post(
        "/api/dict/person",
        json={"name": "张三", "id_card": "110101199001011234"},
        headers=auth(token),
    )
    logs = (await client.get(
        "/api/audit/logs", params={"action": "dict.create"}, headers=auth(token)
    )).json()
    assert logs["total"] >= 1
    entry = logs["items"][0]
    assert entry["target_type"] == "dict_person"
    assert entry["detail"]["values"]["name"] == "张三"


@pytest.mark.asyncio
async def test_audit_logs_require_admin(client, seed_admin):
    admin_token = await get_token(client)
    # create an operator and log in as them
    await client.post(
        "/api/users",
        json={"username": "op1", "password": "op12345", "role": "operator"},
        headers=auth(admin_token),
    )
    op_token = await get_token(client, "op1", "op12345")
    resp = await client.get("/api/audit/logs", headers=auth(op_token))
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_audit_detail_never_contains_password(client, seed_admin):
    """The decisive leak test: create a user with a known password, then assert
    that password string appears nowhere in any audit detail."""
    token = await get_token(client)
    secret = "SuperSecret123"
    await client.post(
        "/api/users",
        json={"username": "leaky", "password": secret, "role": "operator"},
        headers=auth(token),
    )
    # also reset their password through the audited endpoint
    users = (await client.get("/api/users", params={"keyword": "leaky"}, headers=auth(token))).json()
    uid = users["items"][0]["id"]
    await client.post(
        f"/api/users/{uid}/reset-password",
        json={"new_password": "AnotherSecret456"},
        headers=auth(token),
    )

    # Fetch the specific audited actions (not just page 1 of all logs) so the
    # check stays valid regardless of audit volume.
    for action in ("user.create", "user.reset_password"):
        logs = (await client.get(
            "/api/audit/logs", params={"action": action}, headers=auth(token)
        )).json()
        assert logs["total"] >= 1, f"expected an audit row for {action}"
        blob = json.dumps(logs, ensure_ascii=False)
        assert secret not in blob
        assert "AnotherSecret456" not in blob


# ── User management ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_create_user_then_login(client, seed_admin):
    token = await get_token(client)
    resp = await client.post(
        "/api/users",
        json={"username": "newop", "password": "pass1234", "real_name": "新操作员", "role": "operator"},
        headers=auth(token),
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["username"] == "newop"
    assert "password_hash" not in body and "password" not in body
    # the new user can log in
    assert await get_token(client, "newop", "pass1234")


@pytest.mark.asyncio
async def test_create_duplicate_username_409(client, seed_admin):
    token = await get_token(client)
    payload = {"username": "dup", "password": "pass1234", "role": "operator"}
    assert (await client.post("/api/users", json=payload, headers=auth(token))).status_code == 201
    assert (await client.post("/api/users", json=payload, headers=auth(token))).status_code == 409


@pytest.mark.asyncio
async def test_update_user_role(client, seed_admin):
    token = await get_token(client)
    uid = (await client.post(
        "/api/users", json={"username": "promote", "password": "pass1234", "role": "operator"},
        headers=auth(token),
    )).json()["id"]
    resp = await client.put(f"/api/users/{uid}", json={"role": "admin"}, headers=auth(token))
    assert resp.status_code == 200
    assert resp.json()["role"] == "admin"


@pytest.mark.asyncio
async def test_cannot_disable_self(client, seed_admin):
    """The reachable lockout-prevention path: with require_admin the actor is
    always an active admin, so disabling *another* admin always leaves the actor
    behind — the only way to reach zero admins is disabling/demoting yourself,
    which the self-guard blocks."""
    token = await get_token(client)
    me = (await client.get("/api/users", params={"keyword": "admin"}, headers=auth(token))).json()
    admin_id = me["items"][0]["id"]

    disable = await client.put(f"/api/users/{admin_id}", json={"is_active": False}, headers=auth(token))
    assert disable.status_code == 400
    assert "自己" in disable.json()["detail"]

    demote = await client.put(f"/api/users/{admin_id}", json={"role": "operator"}, headers=auth(token))
    assert demote.status_code == 400


@pytest.mark.asyncio
async def test_can_disable_another_admin_when_others_remain(client, seed_admin):
    """Disabling a *different* admin is allowed as long as an active admin
    remains — here the seeded admin remains after disabling admin2."""
    token = await get_token(client)
    uid2 = (await client.post(
        "/api/users", json={"username": "admin2", "password": "pass1234", "role": "admin"},
        headers=auth(token),
    )).json()["id"]
    resp = await client.put(f"/api/users/{uid2}", json={"is_active": False}, headers=auth(token))
    assert resp.status_code == 200
    assert resp.json()["is_active"] is False


@pytest.mark.asyncio
async def test_last_active_admin_guard_helper(seed_admin):
    """Directly exercise the last-active-admin guard, which the API self-guard
    otherwise masks for the only reachable (self) case."""
    from sqlalchemy import select
    from tests.conftest import test_session
    from models.system import SysUser
    from api.users import _is_last_active_admin

    async with test_session() as session:
        admin = (await session.execute(select(SysUser).where(SysUser.username == "admin"))).scalar_one()
        # seeded admin is the only admin → it IS the last active admin
        assert await _is_last_active_admin(session, admin) is True

        # add a second active admin → no longer the last
        session.add(SysUser(username="admin3", password_hash="x", role="admin", is_active=True))
        await session.commit()
        assert await _is_last_active_admin(session, admin) is False
