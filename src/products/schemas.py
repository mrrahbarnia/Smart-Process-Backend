from typing import Annotated
from datetime import datetime
from pydantic import BaseModel, Field

from src.schemas import CustomBaseModel
from src.products.types import CommentId, SerialNumber
from src.admin.types import GuarantySerial


class CommentIn(BaseModel):
    message: str


class CommentList(CommentIn):
    id: CommentId
    username: str
    created_at: Annotated[datetime, Field(serialization_alias="createdAt")]


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
    date_of_document: Annotated[str, Field(alias="dateOfDocument")]
