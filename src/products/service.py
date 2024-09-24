import json
import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from src.pagination import paginate
from src.products.models import Brand, Category
from src.products.config import products_config

async def active_brands(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
) -> list:
    if cached_data := await redis.get("brand-list"):
        return json.loads(cached_data)
    query = sa.select(
        Brand.name, Brand.slug, Brand.description, Brand.is_active
    ).where(Brand.is_active.is_(True))
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()
    result_list = [
        {
            "name": brand.name,
            "slug": brand.slug,
            "description": brand.description,
        } for brand in result
    ]
    await redis.set(
        name="brand-list",
        value=json.dumps(result_list),
        ex=products_config.BRANDS_CACHE_TTL
    )
    return result_list


async def root_categories(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
) -> list:
    if cached_data := await redis.get("root-categories"):
        return json.loads(cached_data)
    query = sa.select(Category.id, Category.name).where(
        sa.and_(
            Category.parent_id.is_(None),
            Category.is_active.is_(True)
        )
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()
    result_list = [
        {
            "id": category.id,
            "name": category.name
        } for category in result
    ]
    await redis.set(
        name="root-categories",
        value=json.dumps(result_list),
        ex=products_config.ROOT_CATEGORIES_CACHE_TTL
    )
    return result_list


async def sub_categories(
        session: async_sessionmaker[AsyncSession],
        redis: Redis,
        parent_id: int
) -> list:
    if cached_data := await redis.get(f"sub-categories:{parent_id}"):
        return json.loads(cached_data)
    query = sa.select(Category.id, Category.name).where(
        sa.and_(
            Category.parent_id==parent_id,
            Category.is_active.is_(True)
        )
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()
    result_list = [
        {
            "id": category.id,
            "name": category.name
        } for category in result
    ]
    if result:
        await redis.set(
            name=f"sub-categories:{parent_id}",
            value=json.dumps(result_list),
            ex=products_config.SUB_CATEGORIES_CACHE_TTL
        )
    return result_list