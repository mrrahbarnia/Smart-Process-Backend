from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from src.database import get_redis, get_session, get_engine
from src.pagination import PaginatedResponse, PaginationQuerySchema, pagination_query
from src.products import service
from src.products import schemas
from src.products.types import (
    ProductId,
    SerialNumber,
    CommentId,
    CommentListResponse,
    UserProductDetailResponse
)
from src.admin.schemas import Brand
from src.admin.types import GuarantySerial
from src.auth.models import User
from src.auth.dependencies import get_current_active_user
from src.admin.schemas import ProductQuerySearch

router = APIRouter()

# ==================== Brands routes ==================== #

@router.get(
    "/active-brands/",
    status_code=status.HTTP_200_OK,
    response_model=list[Brand]
)
async def active_brands(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
):
    result = await service.active_brands(
        session=session,
        redis=redis
    )
    return result

# ==================== Categories routes ==================== #

@router.get(
    "/search-categories/",
    status_code=status.HTTP_200_OK,
    response_model=list[str]
)
async def search_category_by_name(
    category_name: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> list[str]:
    result = await service.search_category_by_name(
        session=session,
        category_name=category_name
    )
    return result


@router.get(
    "/root-categories/",
    status_code=status.HTTP_200_OK
)
async def root_categories(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> list:
    result = await service.root_categories(
        session=session, redis=redis
    )
    return result


@router.get(
    "/sub-categories/{parent_id}/",
    status_code=status.HTTP_200_OK
)
async def sub_categories(
    parent_id: int,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> list:
    result = await service.sub_categories(
        session=session,
        redis=redis,
        parent_id=parent_id
    )
    return result

# ==================== Comments routes ==================== #

@router.post(
    "/create-comment/{product_id}/",
    status_code=status.HTTP_201_CREATED
)
async def create_comment(
    product_id: ProductId,
    payload: schemas.CommentIn,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)]
) -> dict:
    await service.create_comment(
        session=session,
        product_id=product_id,
        payload=payload,
        user_id=user.id
    )
    return {"detail": "Created successfully."}


@router.get(
    "/list-comments/{product_id}/",
    status_code=status.HTTP_200_OK,
    response_model=list[schemas.CommentList]
)
async def list_comments(
    product_id: ProductId,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> list[CommentListResponse]:
    result = await service.list_comments(
        product_id=product_id,
        session=session
    )
    return result


@router.delete(
    "/delete-my-comment/{comment_id}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_my_comment(
    comment_id: CommentId,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    user: Annotated[User, Depends(get_current_active_user)]
) -> None:
    await service.delete_my_comment(
        session=session,
        comment_id=comment_id,
        user_id=user.id
    )

# ==================== Products routes ==================== #

@router.get(
    "/list-products/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.UsersProductList]
)
async def list_products(
    filter_query: Annotated[ProductQuerySearch, Query()],
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)]
) -> dict:
    result = await service.list_products(
        filter_query=filter_query,
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset
    )
    return result


@router.get(
    "/product-detail/{product_serial}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.UsersProductDetail
)
async def product_detail(
    product_serial: SerialNumber,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
) -> UserProductDetailResponse:
    result = await service.product_detail(
        session=session,
        product_serial=product_serial
    )
    return result

# ==================== Guaranty routes ==================== #

@router.get(
    "/inquiry-guaranty/{serial_number}/",
    status_code=status.HTTP_200_OK,
    response_model=schemas.InquiryGuarantyOut
)
async def inquiry_guaranty(
    serial_number: GuarantySerial,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
):
    result = await service.inquiry_guaranty(
        serial_number=serial_number,
        session=session
    )
    return result