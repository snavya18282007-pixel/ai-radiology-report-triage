from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from .config import get_settings


class Base(DeclarativeBase):
    pass


_settings = get_settings()
_engine = create_async_engine(_settings.database_url, pool_pre_ping=True)
_SessionLocal = async_sessionmaker(bind=_engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with _SessionLocal() as session:
        yield session


def get_engine():
    return _engine
