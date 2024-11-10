import asyncio
import logging
import sqlalchemy as sa
import httpx

from redis.asyncio import Redis
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth import schemas
from src.auth import exceptions
from src.auth import utils
from src.auth.config import auth_config
from src.auth.types import Password, UserId, PhoneNumber
from src.auth.models import User

logger = logging.getLogger("auth")


async def send_message(phone_number: PhoneNumber, subject: str):
    url = auth_config.SMS_URL
    api_key = auth_config.SMS_API_KEY
    sender = auth_config.SMS_SENDER
    complete_url = f"{url}/{api_key}/sms/send.json?receptor={phone_number}&sender={sender}&message={subject}"

    async with httpx.AsyncClient() as client:
        response = await client.post(complete_url)
        if response.status_code != 200:
            logger.error("There is an issue in sms service!")
            raise exceptions.MessageServiceError


async def get_user_by_id(
        id: UserId,
        session: async_sessionmaker[AsyncSession]
) -> User:
    query = sa.select(User).where(User.id == id)
    try:
        async with session.begin() as conn:
            user: User | None = await conn.scalar(query)
            if not user:
                raise exceptions.UserNotFound
        return user
    except exceptions.UserNotFound as ex:
        logger.warning(ex)
        raise exceptions.UserNotFound


async def register(
        session: async_sessionmaker[AsyncSession],
        redis: Redis,
        payload: schemas.RegisterIn,
        verification_code: str
) -> bool:
    hashed_password = utils.get_password_hash(password=payload.password)
    query = sa.insert(User).values(
        {
            User.phone_number: payload.phone_number,
            User.username: payload.username,
            User.password: hashed_password,
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
        await redis.set(
            name=f"verification_code:{verification_code}",
            value=payload.phone_number,
            ex=auth_config.VERIFICATION_CODE_LIFE_TIME_SECONDS
        )
    except IntegrityError as ex:
        logger.warning(ex)
        if "uq_users_username" in str(ex):
            raise exceptions.UsernameAlreadyExists
        if "uq_users_phone_number" in str(ex):
            raise exceptions.PhoneNumberAlreadyExists
    return True


async def login(
        session: async_sessionmaker[AsyncSession],
        payload: OAuth2PasswordRequestForm
) -> str:
    query = sa.select(User).where(User.phone_number == payload.username)
    try:
        async with session.begin() as conn:
            user: User | None = (await conn.scalar(query))
            if not user:
                raise exceptions.UserNotFound
        if not utils.verify_password(
            plain_password=payload.password, hashed_password=user.password
        ):
            raise exceptions.UserNotFound
        if user.is_active is False:
            raise exceptions.NotActiveUser
        return utils.encode_access_token(user_id=user.id, user_role=user.role)
    except exceptions.UserNotFound as ex:
        logger.warning(ex)
        raise exceptions.UserNotFound
    except exceptions.NotActiveUser as ex:
        logger.warning(ex)
        raise exceptions.NotActiveUser
    except IntegrityError as ex:
        logger.warning(ex)
        raise exceptions.UserNotFound


async def verify_account(
        session: async_sessionmaker[AsyncSession],
        redis: Redis,
        verification_code: str
) -> None:
    phone_number = await redis.get(
        name=f"verification_code:{verification_code}"
    )
    if not phone_number:
        raise exceptions.InvalidVerificationCode
    query = sa.update(User).where(User.phone_number==phone_number).values(
        {
            User.is_active: True
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        logger.warning(ex)


async def change_password(
        session: async_sessionmaker[AsyncSession],
        user: User,
        payload: schemas.ChangePasswordIn 
) -> None: 
    if not utils.verify_password(
        plain_password=payload.old_password, hashed_password=user.password
    ):
        raise exceptions.WrongOldPassword
    new_hashed_password = utils.get_password_hash(payload.new_password)
    query = sa.update(User).where(User.password==user.password).values(
        {
            User.password: new_hashed_password
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        logger.warning(ex)


async def reset_password(
        session: async_sessionmaker[AsyncSession],
        phone_number: PhoneNumber,
        random_password: str,
        redis: Redis
) -> bool:
    query = sa.select(User.id).where(User.phone_number==phone_number)
    try:
        async with session.begin() as conn:
            user: User | None = await conn.scalar(query)
            if user is None:
                raise exceptions.UserNotFound
        await redis.set(
            name=f"reset_password:{random_password}",
            value=phone_number,
            ex=auth_config.RANDOM_PASSWORD_LIFE_TIME_SECONDS
        )
    except exceptions.UserNotFound as ex:
        logger.warning(ex)
        raise exceptions.UserNotFound
    except Exception as ex:
        logger.warning(ex)
    return True


async def verify_reset_password(
        session: async_sessionmaker[AsyncSession],
        random_password: Password,
        redis: Redis
) -> None:
    phone_number: PhoneNumber | None = await redis.get(
        name=f"reset_password:{random_password}"
    )
    if not phone_number:
        raise exceptions.InvalidRandomPassword
    new_hashed_password = utils.get_password_hash(random_password)
    query = sa.update(User).where(User.phone_number==phone_number).values(
        {
            User.password: new_hashed_password
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        logger.warning(ex)


async def resend_verification_code(
        session: async_sessionmaker[AsyncSession],
        phone_number: PhoneNumber,
        verification_code: str,
        redis: Redis
) -> bool:
    query = sa.select(User.id).where(User.phone_number==phone_number)
    try:
        async with session.begin() as conn:
            result: User | None = await conn.scalar(query)
            if result is None:
                raise exceptions.UserNotFound
        await redis.set(
                name=f"verification_code:{verification_code}",
                value=phone_number,
                ex=auth_config.VERIFICATION_CODE_LIFE_TIME_SECONDS
            )
    except exceptions.UserNotFound as ex:
        logger.warning(ex)
        raise exceptions.UserNotFound
    except Exception as ex:
        logger.warning(ex)
    return True
