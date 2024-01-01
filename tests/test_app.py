import pytest
import pytest_asyncio
from httpx import AsyncClient
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    AsyncEngine,
    async_sessionmaker,
)


from sqlalchemy import select, text, NullPool

from app.main import app
from app.models import Base, User


DATABASE_URL = "postgresql+asyncpg://test_user:passwordtest@localhost:5432/test_db"

# Асинхронный движок для SQLAlchemy
engine_test: AsyncEngine = create_async_engine(DATABASE_URL, poolclass=NullPool)

# Асинхронная фабрика сессий
async_session = async_sessionmaker(
    bind=engine_test, expire_on_commit=False, autoflush=False, autocommit=False
)

client = TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def setup_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


@pytest.mark.asyncio
async def test_user_creation(setup_database):
    async with async_session() as session:
        new_user = User(
            email="test@example.com", password="some_password", username="my_nick"
        )
        session.add(new_user)
        await session.commit()

        result = await session.execute(
            select(User).where(User.email == "test@example.com")
        )
        user = result.scalar_one()
        assert user.username == "my_nick"


@pytest.mark.asyncio
async def test_user_get(async_client):
    async with async_session() as session:
        result = await session.execute(select(User).where(User.id == 1))
        user = result.scalar_one()
        assert user.username == "my_nick"


@pytest.mark.asyncio
async def test_root():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    assert response.status_code == 404
    assert response.json() == {"detail": "Not Found"}
