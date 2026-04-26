import pytest


TRANSACTION_PAYLOAD = {
    "property_name": "Grand Hotel",
    "category": "room booking",
    "price": 150.00,
    "quantity": 2,
    "date": "2026-01-15",
}


@pytest.mark.asyncio
async def test_create_transaction_success(client, auth_headers):
    response = await client.post(
        "/transactions/",
        json=TRANSACTION_PAYLOAD,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["property_name"] == "Grand Hotel"
    assert data["category"] == "room booking"
    assert data["price"] == 150.00
    assert data["quantity"] == 2
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_transaction_invalid_price(client, auth_headers):
    payload = {**TRANSACTION_PAYLOAD, "price": -10}
    response = await client.post(
        "/transactions/",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_transaction_invalid_quantity(client, auth_headers):
    payload = {**TRANSACTION_PAYLOAD, "quantity": 0}
    response = await client.post(
        "/transactions/",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_transaction_no_auth(client):
    response = await client.post("/transactions/", json=TRANSACTION_PAYLOAD)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_bulk_create_success(client, auth_headers):
    payload = {
        "transactions": [
            {
                "property_name": "Ocean Resort",
                "category": "food",
                "price": 45.50,
                "quantity": 4,
                "date": "2026-01-16",
            },
            {
                "property_name": "City Inn",
                "category": "service",
                "price": 30.00,
                "quantity": 1,
                "date": "2026-01-17",
            },
        ]
    }
    response = await client.post(
        "/transactions/bulk",
        json=payload,
        headers=auth_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert len(data) == 2


@pytest.mark.asyncio
async def test_get_transactions_no_filter(client, auth_headers):
    await client.post(
        "/transactions/",
        json=TRANSACTION_PAYLOAD,
        headers=auth_headers,
    )
    response = await client.get(
        "/transactions/",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "skip" in data
    assert "limit" in data


@pytest.mark.asyncio
async def test_get_transactions_filter_category(client, auth_headers):
    response = await client.get(
        "/transactions/?category=room booking",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    for item in data["items"]:
        assert item["category"] == "room booking"


@pytest.mark.asyncio
async def test_get_transactions_pagination(client, auth_headers):
    response = await client.get(
        "/transactions/?skip=0&limit=2",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 2
    assert data["limit"] == 2