import logging
import json
import sqlalchemy as sa

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from redis.asyncio import Redis

from src.pagination import paginate
from src.products import exceptions
from src.products import schemas
from src.products.models import (
    Brand,
    Category,
    Comment,
    Product,
    ProductImage,
    AttributeValue,
    CategoryAttribute,
    Attribute
)
from src.products.types import (
    ProductId,
    CommentId,
    SerialNumber,
    CommentListResponse,
    UserProductDetailResponse
)
from src.products.config import products_config
from src.auth.models import User
from src.auth.types import UserId
from src.admin.models import Guaranty
from src.admin.schemas import ProductQuerySearch
from src.admin.types import GuarantySerial
from src.admin.exceptions import ProductNotFound

logger = logging.getLogger("products")

product_image_subquery = sa.select(
    ProductImage.url,
    ProductImage.product_id
).distinct(ProductImage.product_id).subquery()

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
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
    except Exception as ex:
        logger.warning(ex)
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


async def search_brand_by_name(
        session: async_sessionmaker[AsyncSession],
        brand_name: str
) -> list[str]:
    query = sa.select(Brand.name).where(Brand.name.ilike(f"%{brand_name}%"))
    try:
        async with session.begin() as conn:
            result = (await conn.scalars(query)).all()
    except Exception as ex:
        logger.warning(ex)
    return [brand for brand in result]

# ==================== Category services ==================== #

async def search_category_by_name(
        session: async_sessionmaker[AsyncSession],
        category_name: str
) -> list[str]:
    query = sa.select(Category.name).where(Category.name.ilike(f"%{category_name}%"))
    try:
        async with session.begin() as conn:
            result = (await conn.scalars(query)).all()
    except Exception as ex:
        logger.warning(ex)
    return [cat for cat in result]


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
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
    except Exception as ex:
        logger.warning(ex)
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
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
    except Exception as ex:
        logger.warning(ex)
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

async def list_assigned_attributes(
        category_name: str,
        session: async_sessionmaker[AsyncSession],
) -> list[str]:
    query = (
        sa.select(Attribute.name)
        .select_from(Attribute)
        .join(CategoryAttribute, CategoryAttribute.attribute_name==Attribute.name)
        .join(Category, Category.id==CategoryAttribute.category_id)
        .where(Category.name==category_name)
    )
    try:
        async with session.begin() as conn:
            result = (await conn.scalars(query)).all()
    except Exception as ex:
        logger.warning(ex)
    return [attribute_name for attribute_name in result]

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
    except IntegrityError as ex:
        logger.warning(ex)
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
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
    except Exception as ex:
        logger.warning(ex)
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
    try:
        async with session.begin() as conn:
            result: CommentId | None = await conn.scalar(query)
            if result is None:
                raise exceptions.CommentNotOwner
    except exceptions.CommentNotOwner as ex:
        logger.warning(ex)
        raise exceptions.CommentNotOwner
    except IntegrityError as ex:
        logger.warning(ex)

# ==================== Attribute services ==================== #

async def search_attribute(
        session: async_sessionmaker[AsyncSession],
        attribute_name: str
) -> list[str]:
    query = (
        sa.select(Attribute.name)
        .where(Attribute.name.ilike(f"%{attribute_name}%"))
    )
    try:
        async with session.begin() as conn:
            result = (await conn.scalars(query)).all()
    except Exception as ex:
        logger.warning(ex)
    return [attr for attr in result]

# ==================== Product services ==================== #

async def list_products(
        engine: AsyncEngine,
        filter_query: ProductQuerySearch,
        limit: int,
        offset: int
) -> dict | None:
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
            sa.func.round(
                sa.case(
                (
                    (
                        Product.discount.is_not(None) &
                        Product.expiry_discount.is_not(None) &
                        (Product.expiry_discount >= sa.func.current_date())
                    ),
                    Product.price * (1 - Product.discount / 100)
                ),
                    else_=None
                ), 6
            ).label("price_after_discount"),
            Category.name.label("category_name"),
            Brand.name.label("brand_name"),
            product_image_subquery.c.url.label("image_url")
        )
        .select_from(Product)
        .join(Category, Product.category_id==Category.id)
        .join(Brand, Product.brand_id==Brand.id)
        .join(product_image_subquery, Product.id==product_image_subquery.c.product_id)
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
) -> UserProductDetailResponse:
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
            sa.func.round(
                sa.case(
                (
                    (
                        Product.discount.is_not(None) &
                        Product.expiry_discount.is_not(None) &
                        (Product.expiry_discount >= sa.func.current_date())
                    ),
                    Product.price * (1 - Product.discount / 100)
                ),
                    else_=None
                ), 6
            ).label("price_after_discount"),
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
    update_query = sa.update(Product).values(
        {
            Product.views: Product.views + 1
        }
    ).where(Product.serial_number==product_serial)
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
            await conn.execute(update_query)
    except Exception as ex:
        logger.warning(ex)

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
        "price_after_discount": result[0].price_after_discount,
        "category_name": result[0].category_name,
        "brand_name": result[0].brand_name,
        "image_urls": set([p.image_urls for p in result]),
        "attribute_values": attribute_values
    }


async def most_viewed_products(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    if cached_data := await redis.get("most-viewed-products"):
        return json.loads(cached_data)
    query = (
        sa.select(
            Product.name,
            Product.serial_number,
            Product.views,
            product_image_subquery.c.url.label("image")
        )
        .join(product_image_subquery, Product.id==product_image_subquery.c.product_id)
        .order_by(Product.views.desc())
        .limit(10)
    )
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
            result_list = [
                {
                    "name": product.name,
                    "serial_number": product.serial_number,
                    "views": product.views,
                    "image": product.image
                } for product in result
            ]
            await redis.set(
                name="most-viewed-products",
                value=json.dumps(result_list),
                ex=180
            )
            return result
        
    except Exception as ex:
        logger.warning(ex)


async def newest_products(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    if cached_data := await redis.get("newest-products"):
        return json.loads(cached_data)
    query = (
        sa.select(
            Product.name,
            Product.serial_number,
            Product.created_at,
            product_image_subquery.c.url.label("image")
        )
        .join(product_image_subquery, Product.id==product_image_subquery.c.product_id)
        .order_by(Product.created_at.desc())
        .limit(10)
    )
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).all()
            result_list = [
                {
                    "name": product.name,
                    "serial_number": product.serial_number,
                    "created_at": str(product.created_at),
                    "image": product.image
                } for product in result
            ]
            await redis.set(
                name="newest-products",
                value=json.dumps(result_list),
                ex=1020
            )
            return result

    except Exception as ex:
        logger.warning(ex)

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
    try:
        async with session.begin() as conn:
            guaranty = (await conn.execute(query)).first()
            if guaranty is None:
                raise exceptions.GuarantyNotFound
        return guaranty
    except exceptions.GuarantyNotFound as ex:
        logger.warning(ex)
        raise exceptions.GuarantyNotFound