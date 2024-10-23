from pydantic import Field, field_validator
from typing import Annotated
from datetime import datetime
from decimal import Decimal

from src.schemas import CustomBaseModel
from src.articles.types import ArticleId
from src.articles.config import article_config
from src.s3.config import storage_config


class ArticleBase(CustomBaseModel):
    id: ArticleId
    title: Annotated[str, Field(max_length=200)]
    description: str
    tags: list[str]
    average_rating: Annotated[Decimal, Field(ge=0, le=5)]
    views: int
    created_at: Annotated[datetime, Field(alias="createdAt")]


class ArticlesList(ArticleBase):
    image: str

    @field_validator("description", mode="after")
    @classmethod
    def truncate_description(cls, description: str) -> str:
        splitted_words = description.split()
        truncated_text = ' '.join(splitted_words[:article_config.TRUNCATED_ARTICLE_WORDS])
        return truncated_text

    @field_validator("image", mode="after")
    @classmethod
    def set_image_url(cls, image: str) -> str:
        return f"{storage_config.S3_API}/{image}"


class ArticleDetail(ArticleBase):
    images: list[str]

    @field_validator("images", mode="after")
    @classmethod
    def set_image_url(cls, images: list[str]) -> list[str]:
        images_list = []
        for image in images:
            images_list.append(f"{storage_config.S3_API}/{image}")
        return images_list
