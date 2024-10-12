from typing import NewType, TypedDict
from datetime import datetime
from uuid import UUID
from decimal import Decimal

# ==================== Models types ==================== #

ProductId = NewType("ProductId", UUID)
SerialNumber = NewType("SerialNumber", str)
BrandId = NewType("BrandId", int)
ProductImageId = NewType("ProductImageId", int)
CategoryId = NewType("CategoryId", int)
AttributeValueId = NewType("AttributeValueId", int)
CommentId = NewType("CommentId", int)

# ==================== Query result types ==================== #

class CommentListResponse(TypedDict):
    id: CommentId
    username: str
    message: str
    created_at: datetime


class UserProductDetailResponse(TypedDict):
    id: ProductId
    serial_number: SerialNumber
    is_active: bool
    name: str
    stock: int
    price: Decimal
    discount: int
    description: str
    expiry_discount: datetime
    price_after_discount: Decimal
    category_name: str
    brand_name: str
    image_urls: set[str]
    attribute_values: dict[str, str]
