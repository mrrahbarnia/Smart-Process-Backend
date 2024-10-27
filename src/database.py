import redis.asyncio as redis

from typing import AsyncGenerator
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy import MetaData, INTEGER, String, UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession

from src.constants import DB_NAMING_CONVENTION
from src.config import settings
from src.auth import types as auth_types
from src.products import types as product_types
from src.cart import types as cart_types
from src.sales import types as sale_types
from src.admin import types as admin_types
from src.tickets import types as ticket_types
from src.articles import types as article_types

POSTGRES_URL = str(settings.POSTGRES_URL)

engine: AsyncEngine = create_async_engine(POSTGRES_URL)


class Base(MappedAsDataclass, DeclarativeBase):
    metadata = MetaData(naming_convention=DB_NAMING_CONVENTION)
    type_annotation_map = {
        auth_types.UserId: INTEGER,
        auth_types.UserRole: String,
        auth_types.Password: String,
        auth_types.PhoneNumber: String,
        product_types.ProductId: UUID,
        product_types.SerialNumber: String,
        product_types.BrandId: INTEGER,
        product_types.ProductImageId: INTEGER,
        product_types.CategoryId: INTEGER,
        product_types.AttributeValueId: INTEGER,
        product_types.CommentId: INTEGER,
        sale_types.SaleId: INTEGER,
        cart_types.CartId: INTEGER,
        admin_types.GuarantyId: INTEGER,
        admin_types.GuarantySerial: String,
        ticket_types.TicketId: INTEGER,
        article_types.ArticleId: UUID,
        article_types.ArticleImageId: INTEGER,
        article_types.RatingId: INTEGER,
        article_types.ArticleCommentId: INTEGER,
        article_types.GlossaryId: INTEGER
    }


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
