from typing import Annotated
from pydantic import BaseModel, ConfigDict, Field, computed_field

from src.utils import slugify
from src.schemas import CustomBaseModel
from src.products import types as product_types


class Brand(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "examples": [
            {
                "name": "Hikvision",
                "description": "This is the popular brand, Hikvision"
            }
        ]
    })
    name: str
    description: str

    @computed_field # type: ignore
    @property
    def slug(self) -> str:
        return slugify(self.name)


class BrandList(Brand):
    is_active: bool


class Category(CustomBaseModel):
    name: Annotated[str, Field(max_length=240)]
    description: str
    parent_category_name: Annotated[str | None, Field(alias="parentCategoryName")] = None


class AllCategories(CustomBaseModel):
    id: product_types.CategoryId
    name: str
    description: str
    is_active: bool
    parent_name: Annotated[str | None, Field(alias="parentName")] = None
