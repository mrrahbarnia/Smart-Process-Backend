import json
import sqlalchemy as sa

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from src.pagination import paginate
from src.products import exceptions
from src.products import schemas
from src.products.models import Brand, Category, Comment
from src.products.types import ProductId, CommentId, CommentListResponse
from src.products.config import products_config
from src.auth.models import User
from src.auth.types import UserId

# ==================== Brand services ==================== #

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

# ==================== Category services ==================== #

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

# ==================== Comment services ==================== #

async def create_comment(
        session: async_sessionmaker[AsyncSession],
        product_id: ProductId,
        payload: schemas.CommentIn,
        user_id: UserId
) -> None:
    query = sa.insert(Comment).values(
        {
            Comment.message: payload.message,
            Comment.product_id: product_id,
            Comment.user_id: user_id
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError:
        raise exceptions.CommentNotCreated


async def list_comments(
        session: async_sessionmaker[AsyncSession],
        product_id: ProductId
) -> list[CommentListResponse]:
    query = (
        sa.select(
            Comment.id,
            Comment.message,
            Comment.created_at,
            User.username
        )
        .select_from(Comment)
        .join(User, Comment.user_id==User.id)
        .where(Comment.product_id==product_id)
        .order_by(Comment.created_at.desc())
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()
    return [
        {
            "id": comment.id,
            "username": comment.username,
            "message": comment.message,
            "created_at": comment.created_at
        } for comment in result
    ]


async def delete_my_comment(
        session: async_sessionmaker[AsyncSession],
        comment_id: CommentId,
        user_id: UserId
) -> None:
    query = sa.delete(Comment).where(
        sa.and_(
            Comment.id==comment_id,
            Comment.user_id==user_id
        )
    ).returning(Comment.id)
    async with session.begin() as conn:
        result: CommentId | None = await conn.scalar(query)
    if result is None:
        raise exceptions.CommentNotOwner
