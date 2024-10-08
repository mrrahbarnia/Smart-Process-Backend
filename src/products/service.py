import json
import sqlalchemy as sa

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from src.pagination import paginate
from src.products import exceptions
from src.products import schemas
from src.products.models import Brand, Category, Comment, Product, ProductImage, AttributeValue
from src.products.types import ProductId, CommentId, SerialNumber, CommentListResponse
from src.products.config import products_config
from src.auth.models import User
from src.auth.types import UserId
from src.admin.models import Guaranty
from src.admin.schemas import ProductQuerySearch
from src.admin.types import ProductDetailResponse, GuarantySerial
from src.admin.exceptions import ProductNotFound

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

# ==================== Product services ==================== #

async def list_products(
        engine: AsyncEngine,
        filter_query: ProductQuerySearch,
        limit: int,
        offset: int
) -> dict:
    sub_query = sa.select(
        ProductImage.url,
        ProductImage.product_id
    ).distinct(ProductImage.product_id).subquery()
    query = (
        sa.select(
            Product.id,
            Product.serial_number,
            Product.category_id,
            Product.name,
            Product.stock,
            Product.price,
            Product.discount,
            Product.is_active,
            Category.name.label("category_name"),
            Brand.name.label("brand_name"),
            sub_query.c.url.label("image_url")
        )
        .select_from(Product)
        .join(Category, Product.category_id==Category.id)
        .join(Brand, Product.brand_id==Brand.id)
        .join(sub_query, Product.id==sub_query.c.product_id)
    )

    if filter_query.brand__exact:
        query = query.where(
            sa.and_(
                Brand.name==filter_query.brand__exact,
                Brand.is_active.is_(True)
            )
        )

    if filter_query.category__exact:
        categories_cte = sa.select(
            Category.id,
            Category.name,
            Category.is_active,
            Category.parent_id,
            sa.literal(0).label("level")
        ).where(
            sa.and_(
                Category.name==filter_query.category__exact,
                Category.is_active.is_(True)
            )
        ).cte(recursive=True)

        category_alias = sa.alias(Category) # type: ignore

        recursive_query = sa.select(
            category_alias.c.id,
            category_alias.c.name,
            category_alias.c.is_active,
            category_alias.c.parent_id,
            (categories_cte.c.level + 1).label("level")
        ).join(
            categories_cte, categories_cte.c.id==category_alias.c.parent_id
        )

        categories_cte = categories_cte.union(recursive_query)
        query = query.join(
            categories_cte, Product.category_id==categories_cte.c.id
        ).where(categories_cte.c.is_active.is_(True)).order_by(
            categories_cte.c.level
        )
        

    if filter_query.name__contain:
        query = query.where(
            Product.name.ilike(f"%{filter_query.name__contain}%")
        )

    query = query.where(
        Product.is_active.is_(True),
        Brand.is_active.is_(True),
        Category.is_active.is_(True)
    ).order_by(Product.created_at.desc())

    return await paginate(
        engine=engine, query=query, limit=limit, offset=offset
    )


async def product_detail(
        session: async_sessionmaker[AsyncSession],
        product_serial: SerialNumber,
) -> ProductDetailResponse:
    query = (
        sa.select(
            Product.id,
            Product.serial_number,
            Product.name,
            Product.stock,
            Product.price,
            Product.discount,
            Product.is_active,
            Product.description,
            Product.expiry_discount,
            Category.name.label("category_name"),
            Brand.name.label("brand_name"),
            AttributeValue.attribute_name.label("attribute"),
            AttributeValue.value,
            ProductImage.url.label("image_urls")
        )
        .select_from(Product)
        .join(Category, Product.category_id==Category.id)
        .join(Brand, Product.brand_id==Brand.id)
        .join(ProductImage, Product.id==ProductImage.product_id, isouter=True)
        .join(AttributeValue, Product.id==AttributeValue.product_id, isouter=True)
        .where(
            sa.and_(
                Product.serial_number==product_serial,
                Product.is_active.is_(True),
                Brand.is_active.is_(True),
                Category.is_active.is_(True)
            )
        )
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()

    if len(result) == 0:
        raise ProductNotFound
    attribute_values = dict()
    for p in result:
        if p.attribute not in attribute_values:
            attribute_values[p.attribute] = p.value
    return {
        "id": result[0].id,
        "serial_number": result[0].serial_number,
        "is_active": result[0].is_active,
        "name": result[0].name,
        "stock": result[0].stock,
        "price": result[0].price,
        "discount": result[0].discount,
        "description": result[0].description,
        "expiry_discount": result[0].expiry_discount,
        "category_name": result[0].category_name,
        "brand_name": result[0].brand_name,
        "image_urls": set([p.image_urls for p in result]),
        "attribute_values": attribute_values
    }

# ==================== Guaranty service ==================== #

async def inquiry_guaranty(
        session: async_sessionmaker[AsyncSession],
        serial_number: GuarantySerial,
):
    query = sa.select(
        Guaranty.product_serial_number,
        Guaranty.guaranty_serial,
        Guaranty.product_name,
        Guaranty.guaranty_days,
        Guaranty.produced_at
    ).where(
        Guaranty.guaranty_serial==serial_number
    )
    async with session.begin() as conn:
        guaranty = (await conn.execute(query)).first()
    if guaranty is None:
        raise exceptions.GuarantyNotFound
    return guaranty