from redis.asyncio import Redis
from typing import Annotated
from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.database import get_session, get_redis
from src.cart import service
from src.cart.schemas import AddProductToCartIn
from src.auth.models import User
from src.auth.dependencies import get_current_active_user

router = APIRouter()


@router.put(
    "/update-cart/",
    status_code=status.HTTP_204_NO_CONTENT
)
async def update_cart(
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    payload: AddProductToCartIn,
    redis: Annotated[Redis, Depends(get_redis)],
    user: Annotated[User, Depends(get_current_active_user)]
):
    await service.update_cart(
        session=session,
        user_id=user.id,
        payload=payload,
        redis=redis
    )
