import pytest


@pytest.mark.asyncio
async def test_csv_upload_valid(client, auth_headers):
    csv_content = (
        "property_name,category,price,quantity,date\n"
        "Grand Hotel,room booking,150.00,2,2026-01-15\n"
        "Ocean Resort,food,45.50,4,2026-01-16\n"
        "City Inn,service,30.00,1,2026-01-17\n"
    )
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 3
    assert data["skipped"] == 0
    assert data["errors"] == []


@pytest.mark.asyncio
async def test_csv_upload_mixed_rows(client, auth_headers):
    csv_content = (
        "property_name,category,price,quantity,date\n"
        "Grand Hotel,room booking,150.00,2,2026-02-01\n"
        "Bad Hotel,room booking,-50.00,2,2026-02-02\n"
        "City Inn,service,30.00,bad_qty,2026-02-03\n"
        "Ocean Resort,food,45.50,4,2026-02-04\n"
    )
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 2
    assert data["skipped"] == 2
    assert len(data["errors"]) == 2
    assert data["errors"][0]["row"] == 3
    assert data["errors"][1]["row"] == 4


@pytest.mark.asyncio
async def test_csv_upload_wrong_extension(client, auth_headers):
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.txt", b"some content", "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400
    assert "csv" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_csv_upload_missing_columns(client, auth_headers):
    csv_content = (
        "property_name,price\n"
        "Grand Hotel,150.00\n"
    )
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_csv_upload_empty_file(client, auth_headers):
    csv_content = "property_name,category,price,quantity,date\n"
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 0
    assert data["skipped"] == 0


@pytest.mark.asyncio
async def test_csv_upload_no_auth(client):
    csv_content = "property_name,category,price,quantity,date\n"
    response = await client.post(
        "/transactions/upload-csv",
        files={"file": ("test.csv", csv_content.encode(), "text/csv")},
    )
    assert response.status_code == 403