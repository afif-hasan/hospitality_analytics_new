import pytest


@pytest.mark.asyncio
async def test_register_success(client):
    response = await client.post("/auth/register", json={
        "email": "newuser@test.com",
        "password": "password123",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "newuser@test.com"
    assert data["is_active"] is True
    assert "id" in data
    assert "created_at" in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    await client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "password": "password123",
    })
    response = await client.post("/auth/register", json={
        "email": "duplicate@test.com",
        "password": "password123",
    })
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email(client):
    response = await client.post("/auth/register", json={
        "email": "not-an-email",
        "password": "password123",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(client):
    response = await client.post("/auth/register", json={
        "email": "valid@test.com",
        "password": "abc",
    })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client):
    await client.post("/auth/register", json={
        "email": "logintest@test.com",
        "password": "password123",
    })
    response = await client.post("/auth/login", json={
        "email": "logintest@test.com",
        "password": "password123",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] > 0


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    await client.post("/auth/register", json={
        "email": "wrongpass@test.com",
        "password": "correctpass",
    })
    response = await client.post("/auth/login", json={
        "email": "wrongpass@test.com",
        "password": "wrongpass",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me_success(client, auth_headers):
    response = await client.get("/auth/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "testuser@test.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_get_me_no_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_me_invalid_token(client):
    response = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401