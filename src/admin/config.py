from pydantic_settings import BaseSettings


class AdminConfig(BaseSettings):
    IMAGE_SIZE_LIMIT: int
    IMAGE_FORMAT_LIMIT: str
    MAXIMUM_IMAGES: int

admin_config = AdminConfig() # type: ignore
