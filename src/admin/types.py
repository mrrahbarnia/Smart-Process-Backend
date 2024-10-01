from typing import TypedDict
from decimal import Decimal
from datetime import datetime

from src.products.types import ProductId, SerialNumber


class ProductDetailResponse(TypedDict):
    id: ProductId
    serial_number: SerialNumber
    is_active: bool
    name: str
    stock: int
    price: Decimal
    discount: int
    description: str
    expiry_discount: datetime
    category_name: str
    brand_name: str
    image_urls: set[str]
    attribute_values: dict[str, str]