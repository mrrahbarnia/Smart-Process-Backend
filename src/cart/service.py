import json
import sqlalchemy as sa

from decimal import Decimal
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.cart.models import Cart, CartProduct
from src.cart.config import cart_config
from src.cart.schemas import AddProductToCartIn
from src.cart.types import CartPayloadKeyType, MessageJsonType, CartId
from src.auth.types import UserId


async def create_cart(
        conn: AsyncSession,
        user_id: UserId
) -> None:
    """
    Using this logic in auth service for creating
    user cart's after verify account by them.
    """
    query = sa.insert(Cart).values(
        {
            Cart.user_id: user_id
        }
    )
    await conn.execute(query)


async def update_cart(
        session: async_sessionmaker[AsyncSession],
        redis: Redis,
        user_id: UserId,
        payload: AddProductToCartIn
) -> None:
    payload_cart_data: CartPayloadKeyType = {
        "user_id": str(user_id),
        "total_quantity": payload.total_quantity,
        "total_price": str(payload.total_price)
    }

    cached_cart = await redis.get(name=f"cart:user_id:{user_id}")

    if cached_cart:
        await redis.set(
            name=f"cart:user_id:{user_id}:{json.dumps(payload_cart_data)}",
            value=1,
            ex=cart_config.CART_CACHE_TTL_SEC
        )

    else:
        await redis.set(
            name=f"cart:user_id:{user_id}:{json.dumps(payload_cart_data)}",
            value=1,
            ex=cart_config.CART_CACHE_TTL_SEC
        )

    cart_id_query = sa.select(Cart.id).where(Cart.user_id==user_id)
    async with session.begin() as conn:
        cart_id: CartId | None = await conn.scalar(cart_id_query)
        query = sa.insert(CartProduct).values(
            {
                CartProduct.cart_id: cart_id,
                CartProduct.product_id: payload.product_id
            }
        )
        await conn.execute(query)


async def insert_updated_cart_to_db(
        json_message: MessageJsonType,
        session: async_sessionmaker[AsyncSession]
) -> None:
    query = sa.update(Cart).where(
            Cart.user_id==int(json_message["user_id"])
    ).values(
        {
            Cart.total_quantity: json_message["total_quantity"],
            Cart.total_price: Decimal(json_message["total_price"])
        }
    )
    async with session.begin() as conn:
        await conn.execute(query)
