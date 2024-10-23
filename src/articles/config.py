from pydantic_settings import BaseSettings


class ArticleConfig(BaseSettings):
    TRUNCATED_ARTICLE_WORDS: int

article_config = ArticleConfig() # type: ignore
