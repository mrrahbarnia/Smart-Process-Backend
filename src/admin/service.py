import sqlalchemy as sa

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.admin import schemas
from src.admin import exceptions
from src.products.models import Brand

async def create_brand(
        payload: schemas.Brand,
        session: async_sessionmaker[AsyncSession]
):
    query = sa.insert(Brand).values(
        {
            Brand.name: payload.name,
            Brand.slug: payload.slug,
            Brand.description: payload.description
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        if "uq_brands_name" in str(ex):
            raise exceptions.UniqueConstraintBrandName


async def activate_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession]
):
    query = sa.update(Brand).where(Brand.slug==slug).values(
        {
            Brand.is_active: True
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)


async def deactivate_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession]
):
    query = sa.update(Brand).where(Brand.slug==slug).values(
        {
            Brand.is_active: False
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)


async def delete_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession]
):
    query = sa.delete(Brand).where(Brand.slug==slug)
    async with session.begin() as conn:
        await conn.execute(query)
