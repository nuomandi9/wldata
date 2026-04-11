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
