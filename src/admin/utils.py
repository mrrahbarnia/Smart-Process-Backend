import os

from uuid import uuid4
from fastapi import UploadFile
from typing import BinaryIO

from src.admin import exceptions
from src.admin.config import admin_config


async def validate_images_and_return_unique_image_names(images: list[UploadFile]) -> dict[str, BinaryIO]:
    if len(images) > admin_config.MAXIMUM_IMAGES:
        raise exceptions.MaximumImageNumberExc
    image_valid_ext = admin_config.IMAGE_FORMAT_LIMIT.split(",")
    image_unique_names: dict[str, BinaryIO] = dict()
    for image in images:
        # Validate
        content = await image.read()
        if len(content) > admin_config.IMAGE_SIZE_LIMIT:
            raise exceptions.ImageSizeExc
        if image.content_type not in image_valid_ext:
            raise exceptions.ImageFormatExc
        # Generate unique name
        assert image.filename is not None
        img_ext = os.path.splitext(image.filename)[1]
        image_unique_name = f"{uuid4()}{img_ext}"
        image_unique_names[image_unique_name] = image.file
    return image_unique_names
        