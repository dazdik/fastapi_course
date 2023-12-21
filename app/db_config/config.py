import contextlib
from typing import AsyncIterator

from sqlalchemy.ext.asyncio import (AsyncConnection, AsyncSession,
                                    async_sessionmaker, create_async_engine)

from app.db_config.db_settings import settings

db_url: str = (
    f"postgresql+asyncpg://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:"
    f"{settings.DATABASE_PORT}/{settings.POSTGRES_DB}"
)


class DatabaseSessionManager:
    def __init__(self, url: str, echo: bool = False):
        self.engine = create_async_engine(url=url, echo=echo)
        self.session_factory = async_sessionmaker(
            bind=self.engine, autoflush=False, autocommit=False, expire_on_commit=False
        )

    async def close(self):
        if self.engine is None:
            raise Exception("DatabaseSessionManager не инициализирован")
        await self.engine.dispose()

        self.engine = None
        self.session_factory = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self.engine is None:
            raise Exception("DatabaseSessionManager не инициализирован")

        async with self.engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self.session_factory is None:
            raise Exception("DatabaseSessionManager не инициализирован")

        session = self.session_factory()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(url=db_url, echo=False)


async def get_db_session():
    async with sessionmanager.session() as session:
        yield session
