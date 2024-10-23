from fastapi import APIRouter, Depends, status
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, AsyncEngine

from src.database import get_session
from src.pagination import PaginatedResponse, PaginationQuerySchema, pagination_query
from src.articles import schemas
from src.articles import service

router = APIRouter()


@router.get(
    "/list-articles/",
    status_code=status.HTTP_200_OK,
    response_model=PaginatedResponse[schemas.ArticlesList]
)
async def list_articles(
        engine: Annotated[AsyncEngine, Depends(get_session)],
        pagination_info: Annotated[PaginationQuerySchema, Depends(pagination_query)]
):
    result = await service.list_articles(
        engine=engine,
        limit=pagination_info.limit,
        offset=pagination_info.offset
    )
    return result


    