import sqlalchemy as sa
import sqlalchemy.orm as so

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.admin import schemas
from src.admin import exceptions
from src.pagination import paginate
from src.products.types import CategoryId
from src.products.models import Brand, Category

async def create_brand(
        payload: schemas.Brand,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
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
        await redis.delete("brand-list")
    except IntegrityError as ex:
        if "uq_brands_name" in str(ex):
            raise exceptions.UniqueConstraintBrandName


async def activate_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    query = sa.update(Brand).where(Brand.slug==slug).values(
        {
            Brand.is_active: True
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)
    await redis.delete("brand-list")


async def deactivate_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    query = sa.update(Brand).where(Brand.slug==slug).values(
        {
            Brand.is_active: False
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)
    await redis.delete("brand-list")


async def delete_brand(
        slug: str,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    query = sa.delete(Brand).where(Brand.slug==slug)
    async with session.begin() as conn:
        await conn.execute(query)
    await redis.delete("brand-list")


async def all_brands(engine: AsyncEngine, limit: int, offset: int):
    query = sa.select(
        Brand.name, Brand.slug, Brand.description, Brand.is_active
    )
    return await paginate(
        engine=engine, query=query, limit=limit, offset=offset
    )


async def add_category(
        session: async_sessionmaker[AsyncSession],
        payload: schemas.Category,
        redis: Redis
) -> None:
    if payload.parent_category_name:
        parent_query = sa.select(Category).where(Category.name==payload.parent_category_name)
        async with session.begin() as conn:
            parent_category: Category | None = await conn.scalar(parent_query)
            if parent_category is None:
                raise exceptions.InvalidParentCategoryName
            query = sa.insert(Category).values(
                {
                    Category.name: payload.name,
                    Category.description: payload.description,
                    Category.parent_id: parent_category.id
                }
            )
            try:
                async with session.begin() as conn:
                    await conn.scalars(query)
                await redis.delete("sub-categories:{parent_category.id}")
            except IntegrityError as ex:
                if "uq_categories_name" in str(ex):
                    raise exceptions.DuplicateCategoryName
    else:
        without_parent_query = sa.insert(Category).values(
            {
                Category.name: payload.name,
                Category.description: payload.description
            }
        )
        try:
            async with session.begin() as conn:
                await conn.execute(without_parent_query)
        except IntegrityError as ex:
            if "uq_categories_name" in str(ex):
                raise exceptions.DuplicateCategoryName
        await redis.delete("root-categories")
    


async def all_categories(engine: AsyncEngine, limit: int, offset: int):
    parent_category_table_name = so.aliased(Category)
    parent_category_name = (parent_category_table_name.name).label("parent_name")
    query = (
        sa.select(
            Category.id,
            Category.name,
            Category.description,
            Category.is_active,
            parent_category_name
        )
        .select_from(Category)
        .join(
            parent_category_table_name,
            Category.parent_id==parent_category_table_name.id,
            isouter=True
        )
    ).order_by(Category.created_at.desc())
    return await paginate(engine=engine, query=query, limit=limit, offset=offset)


async def delete_category_by_id(
        session: async_sessionmaker[AsyncSession],
        category_id: CategoryId,
        redis: Redis
) -> None:
    query = sa.delete(Category).where(Category.id==category_id).returning(Category.id)
    async with session.begin() as conn:
        result = await conn.scalar(query)
    if result is None:
        raise exceptions.CategoryNotFound
    await redis.delete("root-categories")
    async for key in redis.scan_iter("sub-categories:*"):
        await redis.delete(key)


async def update_category_by_id(
        session: async_sessionmaker[AsyncSession],
        category_id: CategoryId,
        payload: schemas.Category,
        redis: Redis
):
    if payload.parent_category_name:
        parent_query = sa.select(Category.id).where(
            Category.name==payload.parent_category_name
        )
        async with session.begin() as conn:
            result: CategoryId | None = await conn.scalar(parent_query)
        if result is None:
            raise exceptions.InvalidParentCategoryName
        await redis.delete(f"sub-categories:{result}")
    updated_query = sa.update(Category).where(Category.id==category_id).values(
        {
            Category.name: payload.name,
            Category.parent_id: result if payload.parent_category_name else None
        }
    ).returning(Category.id)
    try:
        async with session.begin() as conn:
            updated_result: CategoryId | None = await conn.scalar(updated_query)
        if updated_result is None:
            raise exceptions.CategoryNotFound
    except IntegrityError as ex:
        if "uq_brands_name" in str(ex):
            raise exceptions.DuplicateCategoryName
    if not payload.parent_category_name:
        await redis.delete("root-categories")


async def search_category_by_name(
        session: async_sessionmaker[AsyncSession],
        category_name: str
) -> list[str]:
    query = sa.select(Category).where(Category.name.ilike(f"%{category_name}%"))
    async with session.begin() as conn:
        result = (await conn.scalars(query)).all()
    return [cat.name for cat in result]


async def activate_category(
        category_id: CategoryId,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
) -> None:
    await redis.delete("root-categories")
    async for key in redis.scan_iter("sub-categories:*"):
        await redis.delete(key)
    query = sa.update(Category).where(Category.id==category_id).values(
        {
            Category.is_active: True
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)


async def deactivate_category(
        category_id: CategoryId,
        session: async_sessionmaker[AsyncSession],
        redis: Redis
) -> None:
    await redis.delete("root-categories")
    async for key in redis.scan_iter("sub-categories:*"):
        await redis.delete(key)
    query = sa.update(Category).where(Category.id==category_id).values(
        {
            Category.is_active: False
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)
