from typing import TypedDict, NewType
from decimal import Decimal
from datetime import datetime

from src.products.types import ProductId, SerialNumber

GuarantyId = NewType("GuarantyId", int)
GuarantySerial = NewType("GuarantySerial", str)

class ExcelEntityTypes(TypedDict):
    product_serial_number: str
    guaranty_serial: str
    product_name: str
    guaranty_days: str
    produced_at: str

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