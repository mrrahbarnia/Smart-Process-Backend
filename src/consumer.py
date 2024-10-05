import os
import json
import asyncio

from io import BytesIO
from dotenv import load_dotenv
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine
)

from cart.types import MessageJsonType # type: ignore
from cart.service import insert_updated_cart_to_db # type: ignore
from admin.service import process_excel_data # type: ignore
from s3.utils import get_obj_from_s3 # type: ignore

load_dotenv()
engine: AsyncEngine = create_async_engine(os.getenv("POSTGRES_URL")) # type: ignore


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
    await pubsub.psubscribe("__keyspace@0__:file:*")
    async for message in pubsub.listen():
        if message["type"] == "pmessage":

            if message["channel"].startswith("__keyspace@0__:cart:user_id"):
                message_list: str = message["channel"].split(":", 4)[-1]
                json_data: MessageJsonType = json.loads(message_list)
                await insert_updated_cart_to_db(
                    json_message=json_data,
                    session=session
                )

            if message["channel"].startswith("__keyspace@0__:file"):
                filename = message["channel"].split(":")[-1]
                file = await get_obj_from_s3(filename=filename)
                await process_excel_data(file=BytesIO(file), session=session)

    await pubsub.close()
    await client.close()


if __name__ == "__main__":
    asyncio.run(listen_to_expired_keys())
