from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.database import get_engine, get_redis, get_session
from src.admin.schemas import Brand, BrandList
from src.products import service

router = APIRouter()


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
