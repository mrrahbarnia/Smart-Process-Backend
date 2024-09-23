from typing import Annotated
from redis.asyncio import Redis
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncEngine

from src.database import get_engine, get_redis
from src.pagination import PaginationQuerySchema, PaginatedResponse, pagination_query
from src.products import schemas
from src.admin.schemas import Brand
from src.products import service

router = APIRouter()


@router.get(
    "/list-brands/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[Brand]
)
async def list_brands(
    engine: Annotated[AsyncEngine, Depends(get_engine)],
    pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)],
):
    result = await service.list_brand(
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset
    )
    return result