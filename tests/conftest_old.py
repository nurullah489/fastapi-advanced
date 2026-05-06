import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.database import Base, get_db
from app.core.config import settings
from app.main import app

#------ Shared fixture for the test database setup and teardown, and HTTP client for testing FastAPI endpoints
#------ Create a new database URL for testing
TEST_DATABASE_URL = settings.database_url.replace("/fastapi_advanced", "/fastapi_advanced_test")

TEST_ENGINE = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(bind=TEST_ENGINE, class_=AsyncSession, expire_on_commit=False)

#------ Override the get_db dependency to use the test database
async def override_get_db():
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise e
        
app.dependency_overrides[get_db] = override_get_db

#------ Create/Drop the test database tables before/after tests
@pytest.fixture(scope="session", autouse=True)
async def setup_database():
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with TEST_ENGINE.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
#------ HTTP client fixture for testing FastAPI endpoints
@pytest.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client
        
#------ Header fixture for authenticated requests
@pytest.fixture
def api_key_header():
    return {"X-API-Key": settings.API_KEY}

@pytest.fixture
async def auth_headers(client, api_key_header):
    # register a test user and get an access token
    register_data = {
        "name": "TestUser",
        "email": "testuser@example.com",
        "password": "testpassword",
        "age": 30
    }
    response = await client.post("/auth/register", json=register_data, headers=api_key_header)
    token = response.json().get("access_token")
    return {"X-API-Key": settings.API_KEY,
            "Authorization": f"Bearer {token}"}  
    
#------ Fixture for registered user id in the database
@pytest.fixture
async def registered_user_id(client, auth_headers):
    register_data = {
        "name": "TestUser2",
        "email": "testuser2@example.com",
        "password": "testpassword",
        "age": 30
    }
    response = await client.post("/auth/register", json=register_data, headers=auth_headers)
    token = response.json().get("access_token")
    headers =  {"X-API-Key": settings.API_KEY,
            "Authorization": f"Bearer {token}"}  
    #------ get user id from endpoint /me ---  this endpoint will return the current authenticated user details 
    # including the id, we can use that id for testing get user by id endpoint
    response = await client.get("/users/me", headers=headers)
    user_id = response.json().get("id")
    return user_id, headers
