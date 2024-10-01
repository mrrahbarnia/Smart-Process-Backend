from pydantic_settings import BaseSettings


class CartConfig(BaseSettings):
    CART_CACHE_TTL_SEC: int

cart_config = CartConfig() # type: ignore
