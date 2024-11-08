from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from decimal import Decimal

from src.schemas import CustomBaseModel
from src.products.types import CommentId, SerialNumber
from src.admin.types import GuarantySerial
from src.admin.schemas import ProductList, ProductDetail
from src.s3.config import storage_config


class CommentIn(BaseModel):
    message: str


class CommentList(CommentIn):
    id: CommentId
    username: str
    created_at: Annotated[datetime, Field(serialization_alias="createdAt")]


class UsersProductList(ProductList):
    price_after_discount: Annotated[Decimal | None, Field(alias="priceAfterDiscount")] = None


class UsersProductDetail(ProductDetail):
    price_after_discount: Annotated[Decimal | None, Field(alias="priceAfterDiscount")] = None


class BaseProduct(CustomBaseModel):
    serial_number: Annotated[SerialNumber, Field(alias="serialNumber")]
    name: Annotated[str, Field(max_length=200)]
    image: str

    @field_validator("image", mode="after")
    @classmethod
    def set_image_url(cls, image: str) -> str:
        return f"{storage_config.S3_API}/{image}"


class MostViewedProducts(BaseProduct):
    views: int


class NewestProducts(BaseProduct):
    created_at: Annotated[datetime, Field(alias="createdAt")]


class InquiryGuarantyOut(CustomBaseModel):
    product_serial_number: Annotated[
        SerialNumber,
        Field(alias="productSerialNumber")
    ]
    guaranty_serial: Annotated[
        GuarantySerial,
        Field(alias="guarantySerial")
    ]
    product_name: Annotated[str, Field(alias="productName")]
    guaranty_days: Annotated[int, Field(alias="guarantyDays")]
    produced_at: Annotated[str, Field(alias="producedAt")]
