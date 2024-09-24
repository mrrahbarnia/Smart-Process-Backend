from pydantic_settings import BaseSettings


class ProductsConfig(BaseSettings):
    BRANDS_CACHE_TTL: int
    ROOT_CATEGORIES_CACHE_TTL: int
    SUB_CATEGORIES_CACHE_TTL: int


products_config = ProductsConfig() # type: ignore