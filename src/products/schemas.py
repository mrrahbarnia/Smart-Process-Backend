from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

from src.schemas import CustomBaseModel
from src.products.types import CommentId, SerialNumber
from src.admin.types import GuarantySerial
from src.admin.schemas import ProductList, ProductDetail


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
