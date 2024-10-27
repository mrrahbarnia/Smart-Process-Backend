import jwt

from uuid import uuid4
from passlib.context import CryptContext # type: ignore
from datetime import timedelta, datetime, timezone

from src.auth.config import auth_config
from src.auth.types import Password, UserId, UserRole

secret_key = auth_config.SECRET_KEY
access_token_life_time = auth_config.ACCESS_TOKEN_EXPIRE_MINUTES
algorithm = auth_config.JWT_ALGORITHM

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def generate_random_code(num: int = 6) -> str:
    """
    Generating random code for resetting
    passwords or some operations like this.
    """
    return uuid4().hex[:num]


def get_password_hash(password: Password) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def encode_access_token(user_id: UserId, user_role: UserRole) -> str:
    payload = {
        "user_id": user_id,
        "user_role": user_role.value,
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=access_token_life_time)
    }
    encoded_jwt = jwt.encode(payload, secret_key, algorithm=algorithm)
    return encoded_jwt
