import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio


async def test_register_success(client: AsyncClient):
    res = await client.post("/api/auth/register", json={
        "email": "user@test.io",
        "password": "Secret123!",
        "full_name": "Jean Dupont",
    })
    assert res.status_code == 201
    data = res.json()
    assert data["email"] == "user@test.io"
    assert data["role"] == "user"
    assert "password_hash" not in data


async def test_register_duplicate_email(client: AsyncClient):
    payload = {"email": "dupe@test.io", "password": "Secret123!"}
    await client.post("/api/auth/register", json=payload)
    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 409


async def test_login_success(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "login@test.io",
        "password": "Secret123!",
    })
    res = await client.post("/api/auth/login", json={
        "email": "login@test.io",
        "password": "Secret123!",
    })
    assert res.status_code == 200
    assert "access_token" in res.json()


async def test_login_wrong_password(client: AsyncClient):
    await client.post("/api/auth/register", json={
        "email": "wrong@test.io",
        "password": "Secret123!",
    })
    res = await client.post("/api/auth/login", json={
        "email": "wrong@test.io",
        "password": "MauvaisMotDePasse",
    })
    assert res.status_code == 401


async def test_me_authenticated(client: AsyncClient, auth_headers: dict):
    res = await client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["email"] == "test@adseason.io"


async def test_me_unauthenticated(client: AsyncClient):
    res = await client.get("/api/auth/me")
    assert res.status_code == 401


async def test_logout(client: AsyncClient, auth_headers: dict):
    res = await client.post("/api/auth/logout", headers=auth_headers)
    assert res.status_code == 200
