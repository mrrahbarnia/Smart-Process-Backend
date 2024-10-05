from typing import NewType, TypedDict

# ==================== Models types ==================== #

CartId = NewType("CartId", int)

# ==================== Cart cache key type ==================== #

class CartPayloadKeyType(TypedDict):
    user_id: str
    total_quantity: int
    total_price: str


class MessageJsonType(TypedDict):
    """
    Type which comes from message broker.
    """
    user_id: str
    total_quantity: str
    total_price: str
