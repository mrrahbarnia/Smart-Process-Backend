from typing import BinaryIO
from aiobotocore.session import get_session # type: ignore

from src.s3.config import storage_config

async def upload_to_s3(file: BinaryIO, unique_filename: str) -> None:
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=storage_config.S3_ENDPOINT,
        aws_access_key_id=storage_config.STORAGE_ACCESS_KEY,
        aws_secret_access_key=storage_config.STORAGE_SECRET_KEY,
    ) as client:
        await client.put_object(
            Bucket=storage_config.BUCKET_NAME,
            Key=unique_filename,
            Body=file
        )


async def delete_from_s3(filename: str):
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=storage_config.S3_ENDPOINT,
        aws_access_key_id=storage_config.STORAGE_ACCESS_KEY,
        aws_secret_access_key=storage_config.STORAGE_SECRET_KEY,
    ) as client:
        await client.delete_object(
            Bucket=storage_config.BUCKET_NAME,
            Key=filename
        )


async def get_obj_from_s3(filename: str) -> BinaryIO:
    session = get_session()
    async with session.create_client(
        "s3",
        endpoint_url=storage_config.S3_ENDPOINT,
        aws_access_key_id=storage_config.STORAGE_ACCESS_KEY,
        aws_secret_access_key=storage_config.STORAGE_SECRET_KEY,
    ) as client:
        response = await client.get_object(
            Bucket=storage_config.BUCKET_NAME,
            Key=filename
        )
        async with response['Body'] as stream:
            file_content = await stream.read()
            return file_content
