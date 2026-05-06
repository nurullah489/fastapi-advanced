import asyncio
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.database import Base, get_db
from app.core.config import settings
from app.main import app


# ---------- TEST DATABASE ----------
TEST_DATABASE_URL = settings.database_url.replace(
    "/fastapi_advanced", "/fastapi_advanced_test"
)

engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=NullPool,  # ensures fresh connection per test
)


# ---------- CREATE/DROP TABLES (ONCE) ----------
@pytest.fixture(scope="session", autouse=True)
def prepare_database():
    async def _setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def _teardown():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

    asyncio.run(_setup())
    yield
    asyncio.run(_teardown())


# ---------- DB SESSION PER TEST (ROLLBACK) ----------
@pytest.fixture
async def db_session():
    async with engine.connect() as conn:
        transaction = await conn.begin()

        session = AsyncSession(bind=conn)

        try:
            yield session
        finally:
            await session.close()
            await transaction.rollback()


# ---------- OVERRIDE DEPENDENCY ----------
@pytest.fixture
def override_get_db(db_session):
    async def _override():
        yield db_session

    app.dependency_overrides[get_db] = _override
    yield
    app.dependency_overrides.clear()


# ---------- CLIENT ----------
@pytest.fixture
async def client(override_get_db):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        follow_redirects=True,
    ) as c:
        yield c


# ---------- AUTH ----------
@pytest.fixture
def api_key_header():
    return {"X-API-Key": settings.API_KEY}


@pytest.fixture
async def auth_headers(client, api_key_header):
    data = {
        "name": "TestUser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "age": 30,
    }

    res = await client.post("/auth/register", json=data, headers=api_key_header)
    assert res.status_code == 201, res.text

    token = res.json()["access_token"]

    return {
        "X-API-Key": settings.API_KEY,
        "Authorization": f"Bearer {token}",
    }


# ---------- USER ----------
@pytest.fixture
async def registered_user_id(client, api_key_header):
    data = {
        "name": "User2",
        "email": "user2@example.com",
        "password": "testpassword",
        "age": 25,
    }

    res = await client.post("/auth/register", json=data, headers=api_key_header)
    token = res.json()["access_token"]

    headers = {
        "X-API-Key": settings.API_KEY,
        "Authorization": f"Bearer {token}",
    }

    me = await client.get("/users/me", headers=headers)

    return me.json()["id"], headers