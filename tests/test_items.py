import pytest

pytestmark = pytest.mark.asyncio


# ---------- CONSTANTS ----------
NON_EXISTENT_ITEM_ID = 9999

ITEM_PAYLOAD = {
    "name": "Test Item",
    "description": "This is a test item",
    "price": 99.99,
    "in_stock": True,
}


# ---------- CREATE ----------
async def test_create_item_success(client, auth_headers):
    response = await client.post("/items/", json=ITEM_PAYLOAD, headers=auth_headers)

    assert response.status_code == 201

    data = response.json()
    assert isinstance(data, dict)

    assert data["name"] == ITEM_PAYLOAD["name"]
    assert data["description"] == ITEM_PAYLOAD["description"]
    assert data["price"] == pytest.approx(ITEM_PAYLOAD["price"])
    assert data["in_stock"] is True
    assert "id" in data


async def test_create_duplicate_item(client, auth_headers):
    payload = {**ITEM_PAYLOAD, "name": "Duplicate Item"}

    await client.post("/items/", json=payload, headers=auth_headers)
    response = await client.post("/items/", json=payload, headers=auth_headers)

    assert response.status_code == 400

    data = response.json()
    assert data["detail"] == "Item with this name already exists"


# ---------- LIST ----------
async def test_list_items(client, auth_headers):
    response = await client.get("/items/", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)

    if data:
        item = data[0]
        assert "id" in item
        assert "name" in item


async def test_items_pagination(client, auth_headers):
    for i in range(15):
        await client.post(
            "/items/",
            json={**ITEM_PAYLOAD, "name": f"Item {i}"},
            headers=auth_headers,
        )

    response = await client.get("/items/?skip=5&limit=5", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 5


async def test_list_items_empty_skip(client, auth_headers):
    response = await client.get("/items/?skip=999999", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert data == []


# ---------- GET ----------
async def test_get_item_not_found(client, auth_headers):
    response = await client.get(f"/items/{NON_EXISTENT_ITEM_ID}", headers=auth_headers)

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == f"Item with id {NON_EXISTENT_ITEM_ID} not found"


async def test_get_item_success(client, auth_headers):
    create_response = await client.post("/items/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = create_response.json()["id"]

    response = await client.get(f"/items/{item_id}", headers=auth_headers)

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == ITEM_PAYLOAD["name"]


# ---------- UPDATE ----------
async def test_update_item_success(client, auth_headers):
    create_response = await client.post("/items/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = create_response.json()["id"]

    update_data = {
        "name": "Updated Item",
        "description": "Updated description",
        "price": 149.99,
        "in_stock": False,
    }

    response = await client.put(
        f"/items/{item_id}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == item_id
    assert data["name"] == update_data["name"]
    assert data["description"] == update_data["description"]
    assert data["price"] == pytest.approx(update_data["price"])
    assert data["in_stock"] is False


async def test_update_item_not_found(client, auth_headers):
    update_data = {
        "name": "Nonexistent Item",
        "description": "This item does not exist",
        "price": 199.99,
        "in_stock": True,
    }

    response = await client.put(
        f"/items/{NON_EXISTENT_ITEM_ID}",
        json=update_data,
        headers=auth_headers,
    )

    assert response.status_code == 404

    data = response.json()
    assert data["detail"] == f"Item with id {NON_EXISTENT_ITEM_ID} not found"


async def test_update_item_invalid_id(client, auth_headers):
    update_data = {
        "name": "Invalid ID Item",
        "description": "Invalid ID",
        "price": 199.99,
        "in_stock": True,
    }

    response = await client.put("/items/invalid_id", json=update_data, headers=auth_headers)

    assert response.status_code == 422

    data = response.json()
    assert "detail" in data


# ---------- DELETE ----------
async def test_delete_item_success(client, auth_headers):
    create_response = await client.post("/items/", json=ITEM_PAYLOAD, headers=auth_headers)
    item_id = create_response.json()["id"]

    response = await client.delete(f"/items/{item_id}", headers=auth_headers)

    assert response.status_code == 204

    # verify deletion
    get_response = await client.get(f"/items/{item_id}", headers=auth_headers)
    assert get_response.status_code == 404


# ---------- AUTH ----------
async def test_create_item_without_api_key(client):
    response = await client.post("/items/", json=ITEM_PAYLOAD)

    assert response.status_code == 401

    data = response.json()
    assert data["detail"] == "Invalid API Key"


async def test_list_items_without_auth(client):
    response = await client.get("/items/")

    assert response.status_code == 401