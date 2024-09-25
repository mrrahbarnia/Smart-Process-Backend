import logging
import sqlalchemy as sa
import sqlalchemy.orm as so

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker
from sqlalchemy.exc import IntegrityError

from src.admin import schemas
from src.admin import exceptions
from src.pagination import paginate
from src.products.types import CategoryId, AttributeId
from src.products.models import (
    Brand,
    Category,
    Attribute,
    CategoryAttribute
)

logger = logging.getLogger("admin")

# ==================== Brand service ==================== #

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

# ==================== Category service ==================== #

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

# ==================== Attribute service ==================== #

async def create_attribute(
        session: async_sessionmaker[AsyncSession],
        payload: schemas.AttributeIn
) -> None:
    query = sa.insert(Attribute).values(
        {
            Attribute.name: payload.name
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        if "uq_attributes_name" in str(ex):
            raise exceptions.DuplicateAttributeName


async def list_attributes(
        engine: AsyncEngine,
        limit: int,
        offset: int,
        name__contain: str | None
) -> dict:
    query = sa.select(Attribute)
    if name__contain:
        query = query.where(Attribute.name.ilike(f"%{name__contain}%"))
    return await paginate(
        query=query, engine=engine, limit=limit, offset=offset
    )


async def delete_attribute(
        attribute_id: AttributeId,
        session: async_sessionmaker[AsyncSession],
) -> None:
    query = (
        sa.delete(Attribute)
        .where(Attribute.id==attribute_id)
        .returning(Attribute.id)
    )
    async with session.begin() as conn:
        result: AttributeId | None = await conn.scalar(query)
    if result is None:
        raise exceptions.AttributeNotFound


async def update_attribute(
        attribute_id: AttributeId,
        session: async_sessionmaker[AsyncSession],
        payload: schemas.AttributeIn
) -> None:
    query = (
        sa.update(Attribute)
        .where(Attribute.id==attribute_id)
        .values(
            {
                "name": payload.name
            }
        )
        .returning(Attribute.id)
    )
    try:
        async with session.begin() as conn:
            result: AttributeId | None = await conn.scalar(query)
        if result is None:
            raise exceptions.AttributeNotFound
    except IntegrityError as ex:
        if "uq_attributes_name" in str(ex):
            raise exceptions.DuplicateAttributeName


async def search_attribute(
        session: async_sessionmaker[AsyncSession],
        attribute_name: str
) -> list[str]:
    query = (
        sa.select(Attribute.name)
        .where(Attribute.name.ilike(f"%{attribute_name}%"))
    )
    async with session.begin() as conn:
        result = (await conn.scalars(query)).all()
    return [attr for attr in result]

# ==================== CategoryAttributes service ==================== #

async def assign_category_attribute(
        session: async_sessionmaker[AsyncSession],
        attribute_name: str,
        category_id: CategoryId,
) -> None:
    attribute_id_query = sa.select(
        Attribute.id
    ).where(Attribute.name==attribute_name)
    async with session.begin() as conn:
        attribute_id: AttributeId | None = await conn.scalar(attribute_id_query)
        if attribute_id is None:
            raise exceptions.AttributeNotFound
        query = sa.insert(CategoryAttribute).values(
            {
                CategoryAttribute.category_id: category_id,
                CategoryAttribute.attribute_id: attribute_id
            }
        )
        try:
            await conn.execute(query)
        except IntegrityError as ex:
            if "fk_categoryattributes_category_id_categories" in str(ex):
                raise exceptions.CategoryNotFound
            if "pk_categoryattributes" in str(ex):
                raise exceptions.CategoryAttributeUniqueTogether


async def unassign_category_attribute(
        session: async_sessionmaker[AsyncSession],
        attribute_name: str,
        category_id: CategoryId,
) -> None:
    attribute_id_query = sa.select(
        Attribute.id
    ).where(Attribute.name==attribute_name)
    async with session.begin() as conn:
        attribute_id: AttributeId | None = await conn.scalar(attribute_id_query)
        if attribute_id is None:
            raise exceptions.AttributeNotFound
        query = sa.delete(CategoryAttribute).where(
            sa.and_(
                CategoryAttribute.category_id==category_id,
                CategoryAttribute.attribute_id==attribute_id
            )
        ).returning(CategoryAttribute.category_id)
        result: CategoryId | None = await conn.scalar(query)
        if result is None:
            raise exceptions.UnassignedWentWrong



