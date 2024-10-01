import os
import json
import asyncio
import sqlalchemy as sa

from decimal import Decimal
from typing import TypedDict
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine
from dotenv import load_dotenv
from redis.asyncio import Redis

from cart.models import Cart # type: ignore

load_dotenv()

engine: AsyncEngine = create_async_engine(os.getenv("POSTGRES_URL")) # type: ignore

class CachedCartData(TypedDict):
    user_id: str
    total_quantity: str
    total_price: str


async def get_session() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine, expire_on_commit=False)


async def listen_to_expired_keys() -> None:
    session = await get_session()
    client = Redis(
        host=os.getenv("REDIS_HOST"), # type: ignore
        port=int(os.getenv("REDIS_PORT")), # type: ignore
        decode_responses=True
    )
    pubsub = client.pubsub()
    await pubsub.psubscribe("__keyspace@0__:cart:*")
    async for message in pubsub.listen():
        if message["type"] == "pmessage":
            if message["channel"].startswith("__keyspace@0__:cart:user_id"):
                message_list: str = message["channel"].split(":", 4)[-1]
                json_data: CachedCartData = json.loads(message_list)

                query = sa.update(Cart).where(Cart.user_id==int(json_data["user_id"])).values(
                    {
                        Cart.total_quantity: json_data["total_quantity"],
                        Cart.total_price: Decimal(json_data["total_price"]),
                        
                    }
                )
                async with session.begin() as conn:
                    await conn.execute(query)

    await pubsub.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(listen_to_expired_keys())
