from asyncio import current_task

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncSession,
                                    async_scoped_session, async_sessionmaker,
                                    create_async_engine)
from typing_extensions import AsyncGenerator

from app.main import app
from app.models import Base, User

DATABASE_URL = "postgresql+asyncpg://test_user:passwordtest@localhost:5432/test_db"
engine = create_async_engine(
    url=DATABASE_URL,
    echo=True,
)


@pytest_asyncio.fixture(scope="session")
async def async_db_connection() -> AsyncGenerator[AsyncConnection, None]:
    async_engine = create_async_engine(
        DATABASE_URL,
        echo=False,
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    conn = await async_engine.connect()
    try:
        yield conn
    except:
        raise
    finally:
        await conn.rollback()

    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await async_engine.dispose()


async def __session_within_transaction(
    async_db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession, None]:
    async_session_maker = async_sessionmaker(
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
        bind=async_db_connection,
        class_=AsyncSession,
    )
    transaction = await async_db_connection.begin()

    yield async_scoped_session(async_session_maker, scopefunc=current_task)

    # все данные откататся
    await transaction.rollback()


@pytest_asyncio.fixture(scope="function")
async def async_db_session(
    async_db_connection: AsyncConnection,
) -> AsyncGenerator[AsyncSession, None]:
    async for session in __session_within_transaction(async_db_connection):
        # setup some data per function
        yield session


@pytest_asyncio.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_users_get(async_client: AsyncClient, async_db_session: AsyncSession):
    # Добавляем пользователя с паролем, так как поле не может быть NULL
    test_user = User(
        username="my_nick", password="some_password", email="test@example.com"
    )
    async_db_session.add(test_user)
    await async_db_session.commit()
    await async_db_session.refresh(test_user)

    response = await async_client.get(f"/user/{test_user.id}")
    assert response.status_code == 200
    assert response.json() == {"username": "my_nick", "email": "test@example.com"}
