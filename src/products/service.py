import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncEngine
from redis.asyncio import Redis

from src.pagination import paginate
from src.products.models import Brand

async def list_brand(
        engine: AsyncEngine,
        limit: int,
        offset: int
):
    query = sa.select(
        Brand.name, Brand.slug, Brand.description
    ).where(Brand.is_active.is_(True))
    return await paginate(
        engine=engine,
        query=query,
        limit=limit,
        offset=offset
    )
