from typing import NewType, TypedDict, Literal

# ==================== Models types ==================== #

CartId = NewType("CartId", int)

# ==================== Cart cache key type ==================== #

class CartPayloadKeyType(TypedDict):
    user_id: str
    total_quantity: int
    total_price: str


# class CacheCartChangeData(TypedDict):
