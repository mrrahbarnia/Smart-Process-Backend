import logging
from redis.asyncio import Redis

from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, status, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.auth.models import User
from src.database import get_session, get_redis
from src.auth import schemas
from src.auth import service
from src.auth.dependencies import get_current_active_user
from src.auth.utils import generate_random_code

logger = logging.getLogger("root")

router = APIRouter()


@router.post(
        "/register/",
        response_model=schemas.RegisterOut,
        status_code=status.HTTP_201_CREATED,
        description="Password must at least has 8 chars."
)
async def register(
    payload: schemas.RegisterIn,
    worker: BackgroundTasks,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> schemas.RegisterOut:
    verification_code = generate_random_code()
    if await service.register(
        session=session,
        redis=redis,
        payload=payload,
        verification_code=verification_code,
    ):
        worker.add_task(service.send_message, payload.phone_number, verification_code)
    return schemas.RegisterOut(
        phone_number=payload.phone_number,
        username=payload.username
    )


@router.post(
    "/login/",
    response_model=schemas.LoginOut,
    status_code=status.HTTP_200_OK
)
async def login(
    payload: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> schemas.LoginOut:
    access_token = await service.login(
        session=session, payload=payload
    )
    return schemas.LoginOut(
        username=payload.username, access_token=access_token, token_type="bearer"
    )


@router.post(
        "/verify-account/",
        status_code=status.HTTP_200_OK
)
async def verify_account(
    payload: schemas.VerificationIn,
    redis: Annotated[Redis, Depends(get_redis)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> dict:
    await service.verify_account(
        session=session,
        redis=redis,
        verification_code=payload.verification_code,
    )
    return {"detail": "Account verified successfully"}


@router.post(
        "/resend/verification-code/",
        status_code=status.HTTP_200_OK
)
async def resend_verification_code(
    payload: schemas.ResendVerificationCode,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    worker: BackgroundTasks,
    redis: Annotated[Redis, Depends(get_redis)]
):
    verification_code = generate_random_code()
    if await service.resend_verification_code(
        session=session,
        phone_number=payload.phone_number,
        verification_code=verification_code,
        redis=redis
    ):
        worker.add_task(service.send_message, payload.phone_number, verification_code)
    return {"detail": "Verification code was resent."}


@router.put(
        "/change-password/",
        status_code=status.HTTP_200_OK
)
async def change_password(
    payload: schemas.ChangePasswordIn,
    active_user: Annotated[User, Depends(get_current_active_user)],
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)]
) -> dict:
    await service.change_password(
        user=active_user,
        session=session,
        payload=payload
    )
    return {"detail": "Password changed successfully"}


@router.post(
        "/reset-password/",
        status_code=status.HTTP_200_OK
)
async def reset_password(
    payload: schemas.ResetPasswordIn,
    worker: BackgroundTasks,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> dict:
    random_password = (generate_random_code(8))
    if await service.reset_password(
        session=session,
        phone_number=payload.phone_number,
        random_password=random_password,
        redis=redis
    ):
        worker.add_task(service.send_message, payload.phone_number, random_password)
    return {"detail": "Temporary password was sent for you."}


@router.post(
        "/reset-password/verify/",
        status_code=status.HTTP_200_OK
)
async def verify_reset_password(
    payload: schemas.VerifyResetPasswordIn,
    session: Annotated[async_sessionmaker[AsyncSession], Depends(get_session)],
    redis: Annotated[Redis, Depends(get_redis)]
) -> dict:
    await service.verify_reset_password(
        session=session,
        random_password=payload.random_password,
        redis=redis
    )
    return {"detail": "Password reset successfully.Change it to your favorite."}
