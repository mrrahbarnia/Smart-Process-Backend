from typing import Annotated, Literal
from pydantic import Field
from decimal import Decimal

from src.schemas import CustomBaseModel
from src.products.types import ProductId


class AddProductToCartIn(CustomBaseModel):
    product_id: Annotated[ProductId | None, Field(alias="productId")] = None
    total_quantity_action: Annotated[
        Literal["increment", "decrement"],
        Field(alias="totalQuantityAction")
    ]
    total_quantity: Annotated[int, Field(alias="totalQuantity")]
    total_price: Annotated[Decimal, Field(alias="totalPrice")]
