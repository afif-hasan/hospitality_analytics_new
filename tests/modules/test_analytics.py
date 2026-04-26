import pytest


@pytest.fixture(autouse=True)
async def seed_data(client, auth_headers):
    transactions = [
        {
            "property_name": "Grand Hotel",
            "category": "room booking",
            "price": 200.00,
            "quantity": 2,
            "date": "2026-01-10",
        },
        {
            "property_name": "Ocean Resort",
            "category": "food",
            "price": 50.00,
            "quantity": 4,
            "date": "2026-01-15",
        },
        {
            "property_name": "Grand Hotel",
            "category": "service",
            "price": 80.00,
            "quantity": 1,
            "date": "2026-02-05",
        },
        {
            "property_name": "City Inn",
            "category": "room booking",
            "price": 120.00,
            "quantity": 3,
            "date": "2026-02-10",
        },
    ]
    for t in transactions:
        await client.post(
            "/transactions/",
            json=t,
            headers=auth_headers,
        )


@pytest.mark.asyncio
async def test_total_sales_no_filter(client, auth_headers):
    response = await client.get(
        "/analytics/total-sales",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert "total_revenue" in data
    assert "total_transactions" in data
    assert "average_order_value" in data
    assert data["total_revenue"] > 0
    assert data["total_transactions"] > 0


@pytest.mark.asyncio
async def test_total_sales_with_date_filter(client, auth_headers):
    response = await client.get(
        "/analytics/total-sales?start_date=2026-02-01&end_date=2026-02-28",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_transactions"] == 2


@pytest.mark.asyncio
async def test_top_properties_no_filter(client, auth_headers):
    response = await client.get(
        "/analytics/top-properties",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3
    assert data[0]["rank"] == 1
    for item in data:
        assert "property_name" in item
        assert "total_revenue" in item
        assert "total_transactions" in item
    revenues = [item["total_revenue"] for item in data]
    assert revenues == sorted(revenues, reverse=True)


@pytest.mark.asyncio
async def test_top_properties_with_date_filter(client, auth_headers):
    response = await client.get(
        "/analytics/top-properties?start_date=2026-01-01&end_date=2026-01-31",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 3


@pytest.mark.asyncio
async def test_category_breakdown(client, auth_headers):
    response = await client.get(
        "/analytics/category-breakdown",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert "category" in item
        assert "total_revenue" in item
        assert "total_transactions" in item
    revenues = [item["total_revenue"] for item in data]
    assert revenues == sorted(revenues, reverse=True)


@pytest.mark.asyncio
async def test_analytics_no_auth(client):
    response = await client.get("/analytics/total-sales")
    assert response.status_code == 403