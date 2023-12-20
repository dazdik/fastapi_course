from pathlib import Path

import aiosqlite
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from .db_settings import settings

# BASE_DIR = Path(__file__).resolve().parent.parent
# DB_PATH = BASE_DIR / "db.sqlite3"

# db_url: str = f"sqlite+aiosqlite:///{DB_PATH}"
db_url: str = f"postgresql+asyncpg://{settings.POSTGRES_USER}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOSTNAME}:{settings.DATABASE_PORT}/{settings.POSTGRES_DB}"


engine = create_async_engine(
    url=db_url,
    echo=False,
)


session = async_sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
    autocommit=False,
)
