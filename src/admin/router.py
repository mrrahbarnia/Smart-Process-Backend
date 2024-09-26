from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from src.database import get_session, get_redis, get_engine
from src.pagination import PaginatedResponse, pagination_query, PaginationQuerySchema
from src.admin import schemas
from src.admin import service
from src.products.types import CategoryId, ProductId
from src.auth.dependencies import is_admin

router = APIRouter()

# ==================== Brand routes ==================== #

@router.post(
    "/create-brand/",
    status_code=status.HTTP_201_CREATED
)
async def create_brand(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    is_admin: Annotated[bool, Depends(is_admin)],
    payload: schemas.Brand,
) -> dict:
    await service.create_brand(session=session, payload=payload, redis=redis)
    return {"detail": "created successfully."}


@router.put(
    "/activate-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def activate_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.activate_brand(session=session, slug=slug, redis=redis)


@router.put(
    "/deactivate-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.deactivate_brand(session=session, slug=slug, redis=redis)


@router.delete(
    "/delete-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.delete_brand(session=session, slug=slug, redis=redis)


@router.get(
        "/all-brands/",
        status_code=status.HTTP_200_OK,
        response_model=PaginatedResponse[schemas.BrandList]
)
async def list_brands(
    is_admin: Annotated[bool, Depends(is_admin)],
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)]
) -> dict:
    result = await service.all_brands(
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset
    )
    return result

# ==================== Category routes ==================== #

@router.post(
    "/create-categories/",
    status_code=status.HTTP_201_CREATED
)
async def create_category(
    payload: schemas.Category,
    is_admin: Annotated[bool, Depends(is_admin)],
    redis: Annotated[Redis, Depends(get_redis)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> dict:
    await service.add_category(session=session, payload=payload, redis=redis)
    return {"detail": "Created successfully."}


@router.get(
    "/all-categories/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.AllCategories],
)
async def list_categories(
    is_admin: Annotated[bool, Depends(is_admin)],
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)]
) -> dict:
    result = await service.all_categories(
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset
    )
    return result


@router.delete(
    "/delete-category/{category_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_category_by_slug(
    category_id: CategoryId,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)],
    is_admin: Annotated[bool, Depends(is_admin)]
):
    await service.delete_category_by_id(
        session=session,
        category_id=category_id,
        redis=redis
    )


@router.put(
    "/update-category/{category_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_category_by_id(
    category_id: CategoryId,
    payload: schemas.Category,
    is_admin: Annotated[bool, Depends(is_admin)],
    redis: Annotated[Redis, Depends(get_redis)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
):
    await service.update_category_by_id(
        session=session,
        category_id=category_id,
        payload=payload,
        redis=redis
    )


@router.get(
    "/search-categories/",
    status_code=status.HTTP_200_OK,
    response_model=list[str]
)
async def search_category_by_name(
    category_name: str,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> list[str]:
    result = await service.search_category_by_name(
        session=session,
        category_name=category_name
    )
    return result


@router.put(
    "/activate-category/{category_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def activate_category(
    category_id: CategoryId,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
    redis: Annotated[Redis, Depends(get_redis)]
):
    await service.activate_category(
        session=session,
        category_id=category_id,
        redis=redis
    )


@router.put(
    "/deactivate-category/{category_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate_category(
    category_id: CategoryId,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
    redis: Annotated[Redis, Depends(get_redis)]
):
    await service.deactivate_category(
        session=session,
        category_id=category_id,
        redis=redis
    )

# ==================== Attribute routes ==================== #

@router.post(
    "/create-attribute/",
    status_code=status.HTTP_201_CREATED
)
async def create_attribute(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
    payload: schemas.Attribute
):
    await service.create_attribute(session=session, payload=payload)
    return {"detail": "Created successfully."}


@router.get(
    "/list-attributes/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.Attribute]
)
async def list_attributes(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    is_admin: Annotated[bool, Depends(is_admin)],
    pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)],
    name__contain: str | None = None,
):
    result = await service.list_attributes(
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset,
        name__contain=name__contain
    )
    return result


@router.delete(
    "/delete-attribute/{attribute_name}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_attribute(
    attribute_name: str,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
):
    await service.delete_attribute(
        session=session, attribute_name=attribute_name
    )


@router.put(
    "/update-attribute/{attribute_name}",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_attribute(
    attribute_name: str,
    payload: schemas.Attribute,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
):
    await service.update_attribute(
        session=session,
        attribute_name=attribute_name,
        payload=payload
    )


@router.get(
        "/search-attribute/",
        status_code=status.HTTP_200_OK
)
async def search_attribute(
    is_admin: Annotated[bool, Depends(is_admin)],
    attribute_name: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> list[str]:
    result = await service.search_attribute(
        session=session, attribute_name=attribute_name
    )
    return result

# ==================== CategoryAttributes routes ==================== #

@router.post(
    "/assign/category/{category_id}/attribute/{attribute_name}/",
    status_code=status.HTTP_201_CREATED
)
async def assign_category_attribute(
    category_id: CategoryId,
    attribute_name: str,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> dict:
    await service.assign_category_attribute(
        session=session,
        category_id=category_id,
        attribute_name=attribute_name
    )
    return {"detail": "Assigned successfully."}


@router.delete(
    "/unassigned/category/{category_id}/attribute/{attribute_name}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def unassigned_category_attribute(
    category_id: CategoryId,
    attribute_name: str,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> None:
    await service.unassign_category_attribute(
        session=session,
        category_id=category_id,
        attribute_name=attribute_name
    )


@router.get(
    "/list-assigned-attributes/{category_id}/",
    status_code=status.HTTP_200_OK
)
async def list_assigned_attributes(
    category_id: CategoryId,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> list[str]:
    result = await service.list_assigned_attributes(
        category_id=category_id,
        session=session
    )
    return result

# ==================== Products routes ==================== #

@router.post(
    "/create-product/",
    status_code=status.HTTP_201_CREATED
)
async def create_product(
    payload: schemas.ProductIn,
    images: list[UploadFile],
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
):
    await service.create_product(
        session=session,
        payload=payload,
        images=images
    )
    return {"detail": "Created successfully."}


@router.put(
    "/activate-product/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def activate_product(
    product_id: ProductId,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> None:
    await service.activate_product(
        session=session,
        product_id=product_id
    )


@router.put(
    "/deactivate-product/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate_product(
    product_id: ProductId,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> None:
    await service.deactivate_product(
        session=session,
        product_id=product_id
    )


@router.delete(
    "/delete-product/{product_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_product(
    product_id: ProductId,
    is_admin: Annotated[bool, Depends(is_admin)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> None:
    await service.delete_product(
        session=session,
        product_id=product_id
    )
