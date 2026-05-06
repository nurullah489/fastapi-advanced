import pytest

pytestmark = pytest.mark.asyncio


# ---------- CONSTANTS ----------
REGISTER_PAYLOAD = {
    "name": "Test User",
    "email": "testuser@example.com",
    "password": "securepass123",
    "age": 36,
}


# ---------- REGISTER ----------
async def test_register_success(client, api_key_header):
    payload = {**REGISTER_PAYLOAD, "email": "unique@example.com"}

    response = await client.post("/auth/register", json=payload, headers=api_key_header)

    assert response.status_code == 201

    data = response.json()
    assert isinstance(data, dict)
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_register_duplicate_email(client, api_key_header):
    payload = {**REGISTER_PAYLOAD, "email": "duplicate@test.com"}

    # first call
    res1 = await client.post("/auth/register", json=payload, headers=api_key_header)
    assert res1.status_code == 201

    # duplicate
    res2 = await client.post("/auth/register", json=payload, headers=api_key_header)

    assert res2.status_code == 400

    data = res2.json()
    assert data["detail"] == "User with this email already exists"


async def test_register_invalid_api_key(client):
    payload = {**REGISTER_PAYLOAD, "email": "invalidkey@example.com"}

    response = await client.post(
        "/auth/register",
        json=payload,
        headers={"X-API-Key": "invalid_api_key"},
    )

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


async def test_register_missing_api_key(client):
    payload = {**REGISTER_PAYLOAD, "email": "noapikey@example.com"}

    response = await client.post("/auth/register", json=payload)

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data


# ---------- LOGIN ----------
async def test_login_success(client, api_key_header):
    payload = {**REGISTER_PAYLOAD, "email": "loginuser@example.com"}

    # register first
    res = await client.post("/auth/register", json=payload, headers=api_key_header)
    assert res.status_code == 201

    login_data = {
        "email": payload["email"],
        "password": payload["password"],
    }

    response = await client.post("/auth/login", json=login_data, headers=api_key_header)

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


async def test_login_wrong_password(client, api_key_header):
    payload = {**REGISTER_PAYLOAD, "email": "wrongpass@example.com"}

    await client.post("/auth/register", json=payload, headers=api_key_header)

    login_data = {
        "email": payload["email"],
        "password": "wrongpassword",
    }

    response = await client.post("/auth/login", json=login_data, headers=api_key_header)

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Invalid email or password"


async def test_login_nonexistent_user(client, api_key_header):
    login_data = {
        "email": "nonexistent@example.com",
        "password": "securepass123",
    }

    response = await client.post("/auth/login", json=login_data, headers=api_key_header)

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Invalid email or password"


async def test_login_invalid_api_key(client):
    login_data = {
        "email": "any@example.com",
        "password": "securepass123",
    }

    response = await client.post(
        "/auth/login",
        json=login_data,
        headers={"X-API-Key": "invalid_api_key"},
    )

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data