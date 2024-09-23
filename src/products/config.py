from pydantic_settings import BaseSettings


class ProductsConfig(BaseSettings):
    BRAND_PAGE_LIMIT: int


products_config = ProductsConfig() # type: ignore