import pytest

pytestmark = pytest.mark.asyncio  # applies to all tests


# ---------- CONSTANTS ----------
NON_EXISTENT_USER_ID = 9999


# ---------- ME ----------
async def test_get_me_success(client, auth_headers):
    response = await client.get("/users/me", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, dict)

    assert "id" in data
    assert "email" in data
    assert "hashed_password" not in data  # security check


async def test_get_me_no_token(client, api_key_header):
    response = await client.get("/users/me", headers=api_key_header)

    assert response.status_code == 401

    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Authorization token missing or invalid"


async def test_get_me_invalid_token(client, api_key_header):
    headers = {**api_key_header, "Authorization": "Bearer invalid_token"}

    response = await client.get("/users/me", headers=headers)

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Invalid or expired token"


# ---------- LIST USERS ----------
async def test_list_users(client, auth_headers):
    response = await client.get("/users", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:  # optional deeper validation
        user = data[0]
        assert "id" in user
        assert "email" in user


# ---------- GET USER ----------
async def test_get_user_not_found(client, auth_headers):
    response = await client.get(f"/users/{NON_EXISTENT_USER_ID}", headers=auth_headers)

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == f"User {NON_EXISTENT_USER_ID} not found"


async def test_get_user_success(client, auth_headers, registered_user_id):
    user_id, _ = registered_user_id

    response = await client.get(f"/users/{user_id}", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert "email" in data


async def test_get_user_invalid_id(client, auth_headers):
    response = await client.get("/users/invalid_id", headers=auth_headers)

    assert response.status_code == 422  # validation error

    data = response.json()
    assert "detail" in data


# ---------- UPDATE ----------
async def test_update_own_user(client, registered_user_id):
    user_id, headers = registered_user_id

    update_data = {
        "name": "Updated Name",
        "email": "updated@example.com",
        "age": 25,
        "active": True,
    }

    response = await client.put(
        f"/users/{user_id}",
        json=update_data,
        headers=headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user_id
    assert data["name"] == update_data["name"]
    assert data["email"] == update_data["email"]
    assert data["age"] == update_data["age"]
    assert data["active"] is True


async def test_update_other_user_forbidden(client, auth_headers, registered_user_id):
    user_id, _ = registered_user_id

    hacker_data = {
        "name": "Hacker",
        "email": "owner@test.com",
        "age": 26,
        "active": True,
    }

    response = await client.put(
        f"/users/{user_id}",
        json=hacker_data,
        headers=auth_headers,
    )

    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "You can only update your own profile"


# ---------- DELETE ----------
async def test_delete_other_user_forbidden(client, auth_headers, registered_user_id):
    user_id, _ = registered_user_id

    response = await client.delete(f"/users/{user_id}", headers=auth_headers)

    assert response.status_code == 403

    data = response.json()
    assert data["detail"] == "You can only delete your own profile"