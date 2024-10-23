import sqlalchemy as sa
import sqlalchemy.orm as so

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from src.pagination import paginate
from src.articles import exceptions
from src.articles.models import Article, Rating, Tag, ArticleTag, ArticleImage
from src.articles.types import ArticleId


async def list_articles(
        engine: AsyncEngine,
        limit: int,
        offset: int
):
    image_cte = sa.select(
        ArticleImage.article_id.label("image_article_id"),
        (sa.func.min(ArticleImage.url)).label("image")
    ).group_by(ArticleImage.article_id).cte()
    rating_cte = sa.select(
        Rating.article_id.label("rating_article_id"),
        sa.func.avg(Rating.rating).label("average_rating")
    ).group_by(Rating.article_id).cte()
    query = (
        sa.select(
            Article.id,
            Article.title,
            Article.description,
            Article.views,
            Article.created_at,
            rating_cte.c.average_rating,
            sa.func.array_agg(Tag.name).label("tags"),
            image_cte.c.image
        )
        .select_from(Article)
        .join(ArticleTag, Article.id==ArticleTag.article_id)
        .join(Tag, Tag.id==ArticleTag.tag_id)
        .join(rating_cte, Article.id==rating_cte.c.rating_article_id)
        .join(image_cte, Article.id==image_cte.c.image_article_id)
        .group_by(
            Article.id,
            rating_cte.c.average_rating,
            image_cte.c.image
        )
    )
    result = await paginate(engine=engine, query=query, limit=limit, offset=offset)
    return result


async def article_detail(
        session: async_sessionmaker[AsyncSession],
        article_id: ArticleId
):
    rating_cte = sa.select(
        Rating.article_id,
        sa.func.avg(Rating.rating).label("average_rating")
    ).group_by(Rating.article_id).cte()
    query = (
        sa.select(
            Article.id,
            Article.title,
            Article.description,
            Article.views,
            Article.created_at,
            rating_cte.c.average_rating,
            sa.func.array_agg(sa.func.distinct(ArticleImage.url)).label("images"),
            sa.func.array_agg(sa.func.distinct(Tag.name)).label("tags"),
        )
        .select_from(Article)
        .join(rating_cte, Article.id==rating_cte.c.article_id)
        .join(ArticleImage, Article.id==ArticleImage.article_id)
        .join(ArticleTag, Article.id==ArticleTag.article_id)
        .join(Tag, ArticleTag.tag_id==Tag.id)
        .group_by(
            Article.id,
            Article.title,
            Article.description,
            Article.views,
            Article.created_at,
            rating_cte.c.average_rating,
        )
        .where(Article.id==article_id)
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).first()
    if result is not None:
        return result._asdict()
    else:
        raise exceptions.ArticleNotFound

