from pydantic_settings import BaseSettings


class AuthConfig(BaseSettings):
    PASSWORD_PATTERN: str
    SECRET_KEY: str
    JWT_ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    VERIFICATION_CODE_LIFE_TIME_SECONDS: int
    RANDOM_PASSWORD_LIFE_TIME_SECONDS: int
    # SMS_URL: str
    # SMS_TOKEN: str
    # SMS_FROM: str


auth_config = AuthConfig() # type: ignore
