from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from src.database import get_session, get_redis, get_engine
# from src.pagination import PaginatedResponse, pagination_query, PaginationQuerySchema
from src.admin import schemas
from src.admin import service
from src.auth.dependencies import is_admin

router = APIRouter()

@router.post(
    "/create-brand/",
    status_code=status.HTTP_201_CREATED
)
async def create_brand(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
    payload: schemas.Brand,
) -> dict:
    await service.create_brand(session=session, payload=payload)
    return {"detail": "created successfully."}


@router.put(
    "/activate-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def activate_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.activate_brand(session=session, slug=slug)


@router.put(
    "/deactivate-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def deactivate_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.deactivate_brand(session=session, slug=slug)


@router.delete(
    "/delete-brand/{slug}/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_brand(
    slug: str,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    is_admin: Annotated[bool, Depends(is_admin)],
):
    await service.delete_brand(session=session, slug=slug)
