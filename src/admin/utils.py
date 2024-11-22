import os

from uuid import uuid4
from fastapi import UploadFile
from typing import BinaryIO

from src.admin import exceptions
from src.admin.config import admin_config


async def create_unique_excel_name(file: UploadFile) -> str:
    assert file.filename is not None
    file_ext = os.path.splitext(file.filename)[1]
    file_unique_name = f"{uuid4()}{file_ext}"
    return file_unique_name


async def validate_images_and_return_unique_image_names(images: list[UploadFile]) -> dict[str, BinaryIO]:
    if len(images) > admin_config.MAXIMUM_IMAGES:
        raise exceptions.MaximumImageNumberExc
    image_unique_names: dict[str, BinaryIO] = dict()
    for image in images:
        # Generate unique name
        assert image.filename is not None
        img_ext = os.path.splitext(image.filename)[1]
        image_unique_name = f"{uuid4()}{img_ext}"
        image.file.seek(0)
        image_unique_names[image_unique_name] = image.file
    return image_unique_names


async def return_unique_image_names(images: list[UploadFile]) -> dict[str, BinaryIO]:
    image_unique_names: dict[str, BinaryIO] = dict()
    for image in images:
        # Generate unique name
        assert image.filename is not None
        img_ext = os.path.splitext(image.filename)[1]
        image_unique_name = f"{uuid4()}{img_ext}"
        image.file.seek(0)
        image_unique_names[image_unique_name] = image.file
    return image_unique_names