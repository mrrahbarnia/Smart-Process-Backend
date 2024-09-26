from pydantic_settings import BaseSettings


class StorageConfig(BaseSettings):
    S3_API: str
    S3_ENDPOINT: str
    BUCKET_NAME: str
    STORAGE_ACCESS_KEY: str
    STORAGE_SECRET_KEY: str

storage_config = StorageConfig() # type: ignore
