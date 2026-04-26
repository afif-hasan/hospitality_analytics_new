import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.main import app
from app.core.database import Base
from app.core.dependencies import get_db

TEST_DATABASE_URL = "sqlite+aiosqlite:///./data/test.db"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        from app.modules.auth.model import User            # noqa: F401
        from app.modules.transactions.model import Transaction  # noqa: F401
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def db_session(test_engine):
    AsyncTestSession = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with AsyncTestSession() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture(scope="function")
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client):
    await client.post("/auth/register", json={
        "email": "testuser@test.com",
        "password": "testpass123",
    })
    response = await client.post("/auth/login", json={
        "email": "testuser@test.com",
        "password": "testpass123",
    })
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}