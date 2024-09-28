from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database import get_redis, get_session
from src.products import service
from src.products import schemas
from src.products.types import ProductId, CommentId, CommentListResponse
from src.admin.schemas import Brand
from src.auth.models import User
from src.auth.dependencies import get_current_active_user

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