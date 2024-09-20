import redis.asyncio as redis

from typing import AsyncGenerator
from functools import lru_cache
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import MetaData, INTEGER, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from src.constants import DB_NAMING_CONVENTION
from src.config import settings
from src.auth import types

POSTGRES_URL = str(settings.POSTGRES_URL)

engine: AsyncEngine = create_async_engine(POSTGRES_URL)


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        types.UserId: INTEGER,
        types.UserRule: String,
        types.Password: String,
        types.PhoneNumber: String
    }


@lru_cache
def get_engine() -> AsyncEngine:
    return engine


async def get_session() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    redis_client = redis.Redis(
        host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True
    )
    try:
        yield redis_client
    finally:
        await redis_client.aclose()
