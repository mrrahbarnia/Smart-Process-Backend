import json

from typing import Annotated, Any
from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator
from decimal import Decimal
from datetime import date

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


class Attribute(BaseModel):
    name: Annotated[str, Field(max_length=200)]


class AttributeValueIn(BaseModel):
    attribute: Annotated[str, Field(max_length=200)]
    value: Annotated[str | None, Field(max_length=200)] = None


class ProductIn(CustomBaseModel):
    serial_number: product_types.SerialNumber
    name: Annotated[str, Field(max_length=200)]
    description: str
    stock: Annotated[int, Field(ge=0)]
    price: Annotated[Decimal, Field(ge=0)]
    discount: Annotated[Decimal | None, Field(ge=0, le=100)] = None
    expiry_discount: Annotated[date | None, Field(alias="expiryDiscount")] = None
    attribute_values: Annotated[list[AttributeValueIn], Field(alias="attributeValues")]
    category_name: Annotated[str, Field(alias="categoryName", max_length=150)]
    brand_name: Annotated[str, Field(alias="brandName", max_length=200)]

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value) -> Any:
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
