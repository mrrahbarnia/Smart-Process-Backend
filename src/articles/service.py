import logging
import sqlalchemy as sa
import json

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.dialects.postgresql import insert as postgres_insert

from src.pagination import paginate
from src.articles import exceptions
from src.articles.models import (
    Article,
    Rating,
    Tag,
    ArticleTag,
    ArticleImage,
    GlossaryTerm,
    ArticleComment
)
from src.articles.types import ArticleId, GlossaryId, ArticleCommentId
from src.auth.models import User
from src.auth.types import UserId
from src.products.schemas import CommentIn
from src.products.types import CommentListResponse
from src.products.exceptions import CommentNotCreated, CommentNotOwner

logger = logging.getLogger("articles")

rating_cte = sa.select(
    Rating.article_id.label("rating_article_id"),
    sa.func.avg(Rating.rating).label("average_rating")
).group_by(Rating.article_id).cte()

image_cte = sa.select(
    ArticleImage.article_id.label("image_article_id"),
    (sa.func.min(ArticleImage.url)).label("image")
).group_by(ArticleImage.article_id).cte()

# ==================== Article service ==================== #

async def list_articles(
        engine: AsyncEngine,
        limit: int,
        offset: int
) -> dict | None:
    
    query = (
        sa.select(
            Article.id,
            Article.title,
            Article.description,
            Article.created_at,
            rating_cte.c.average_rating,
            sa.func.array_agg(Tag.name).label("tags"),
            image_cte.c.image
        )
        .select_from(Article)

        # TODO: inner join for images
    
        .join(ArticleTag, Article.id==ArticleTag.article_id, isouter=True)
        .join(Tag, Tag.name==ArticleTag.tag_name, isouter=True)
        .join(rating_cte, Article.id==rating_cte.c.rating_article_id, isouter=True)
        .join(image_cte, Article.id==image_cte.c.image_article_id, isouter=True)
        .group_by(
            Article.id,
            rating_cte.c.average_rating,
            image_cte.c.image
        ).order_by(Article.created_at.desc())
    )
    result = await paginate(engine=engine, query=query, limit=limit, offset=offset)
    if result:
        return result
    return None


async def article_detail(
        session: async_sessionmaker[AsyncSession],
        article_id: ArticleId
) -> dict | None:
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
        .join(rating_cte, Article.id==rating_cte.c.rating_article_id, isouter=True)
        .join(ArticleImage, Article.id==ArticleImage.article_id, isouter=True)
        .join(ArticleTag, Article.id==ArticleTag.article_id, isouter=True)
        .join(Tag, ArticleTag.tag_name==Tag.name, isouter=True)
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
    update_views_query = sa.update(Article).values(
        {
            Article.views: Article.views + 1
        }
    ).where(Article.id==article_id)
    try:
        async with session.begin() as conn:
            result = (await conn.execute(query)).first()
            await conn.execute(update_views_query)
            if result is not None:
                return result._asdict()
            else:
                raise exceptions.ArticleNotFound
    
    except exceptions.ArticleNotFound as ex:
        logger.info(ex)
        return None

    except IntegrityError as ex:
        logger.warning(ex)
        return None


async def newest_articles(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    if cached_data := await redis.get(name="newest_articles"):
        return json.loads(cached_data)
    query = (
        sa.select(
            Article.id,
            Article.title,
            Article.created_at,
            image_cte.c.image
        )
        .select_from(Article)
        .join(image_cte, Article.id==image_cte.c.image_article_id)
        .order_by(Article.created_at.desc())
        .limit(10)
    )
    async with session.begin() as conn:
        articles = (await conn.execute(query)).all()
    articles_list = [
        {
            "id": str(article.id),
            "title": article.title,
            "created_at": str(article.created_at),
            "image": article.image
        } for article in articles
    ]
    await redis.set(
        name="newest_articles",
        value=json.dumps(articles_list),
        ex=180   
    )
    return articles


async def popular_articles(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    if cached_data := await redis.get(name="popular_articles"):
        return json.loads(cached_data)
    query = (
        sa.select(
            Article.id,
            Article.title,
            rating_cte.c.average_rating,
            image_cte.c.image
        )
        .select_from(Article)
        .join(rating_cte, Article.id==rating_cte.c.rating_article_id, isouter=True)
        .join(image_cte, Article.id==image_cte.c.image_article_id)
        .order_by(rating_cte.c.average_rating.desc())
        .limit(10)
    )
    async with session.begin() as conn:
        articles = (await conn.execute(query)).all()
    articles_list = [
        {
            "id": str(article.id),
            "title": article.title,
            "average_rating": article.average_rating,
            "image": article.image
        } for article in articles
    ]
    await redis.set(
        name="popular_articles",
        value=json.dumps(articles_list),
        ex=180   
    )
    return articles


async def most_viewed_articles(
        session: async_sessionmaker[AsyncSession],
        redis: Redis
):
    if cached_data := await redis.get(name="most_viewed_articles"):
        return json.loads(cached_data)
    query = (
        sa.select(
            Article.id,
            Article.title,
            Article.views,
            image_cte.c.image
        )
        .select_from(Article)
        .join(image_cte, Article.id==image_cte.c.image_article_id)
        .order_by(Article.views.desc())
        .limit(10)
    )
    async with session.begin() as conn:
        articles = (await conn.execute(query)).all()
    articles_list = [
        {
            "id": str(article.id),
            "title": article.title,
            "views": str(article.views),
            "image": article.image
        } for article in articles
    ]
    await redis.set(
        name="most_viewed_articles",
        value=json.dumps(articles_list),
        ex=180   
    )
    return articles

# ==================== Rating service ==================== #

async def rating_article(
        session: async_sessionmaker[AsyncSession],
        article_id: ArticleId,
        user_id: UserId,
        rating: int
) -> None:
    query = postgres_insert(Rating).values({
        Rating.rating: rating,
        Rating.user_id: user_id,
        Rating.article_id: article_id
    })
    do_update_stmt = query.on_conflict_do_update(
        constraint="uq_ratings_user_id",
        set_={Rating.rating: rating}
    )
    try:
        async with session.begin() as conn:
            await conn.execute(do_update_stmt)
    except Exception as ex:
        logger.warning(ex)

# ==================== Tag service ==================== #

async def search_tag_by_name(
        session: async_sessionmaker[AsyncSession],
        tag_name: str
) -> list[str]:
    query = sa.select(Tag.name).where(Tag.name.ilike(f"%{tag_name}%"))
    async with session.begin() as conn:
        result = (await conn.scalars(query)).all()
        return [tag for tag in result]

# ==================== Glossary service ==================== #

async def get_glossaries(
        article_id: ArticleId,
        session: async_sessionmaker[AsyncSession]
):
    query = (
        sa.select(GlossaryTerm.id, GlossaryTerm.term, GlossaryTerm.definition)
        .where(GlossaryTerm.article_id==article_id)
    )
    async with session.begin() as conn:
        glossaries = (await conn.execute(query)).all()
        return glossaries


async def get_glossary_by_id(
        glossary_id: GlossaryId,
        session: async_sessionmaker[AsyncSession]
):
    query = (
        sa.select(GlossaryTerm.id, GlossaryTerm.term, GlossaryTerm.definition)
        .where(GlossaryTerm.id==glossary_id)
    )
    async with session.begin() as conn:
        glossary = (await conn.execute(query)).first()
        return glossary

# ==================== Comment service ==================== #

async def create_article_comment(
        session: async_sessionmaker[AsyncSession],
        article_id: ArticleId,
        payload: CommentIn,
        user_id: UserId
) -> None:
    query = sa.insert(ArticleComment).values(
        {
            ArticleComment.message: payload.message,
            ArticleComment.article_id: article_id,
            ArticleComment.user_id: user_id
        }
    )
    try:
        async with session.begin() as conn:
            await conn.execute(query)
    except IntegrityError as ex:
        logger.warning(ex)
        raise CommentNotCreated


async def list_article_comments(
        session: async_sessionmaker[AsyncSession],
        article_id: ArticleId
) -> list[CommentListResponse]:
    query = (
        sa.select(
            ArticleComment.id,
            ArticleComment.message,
            ArticleComment.created_at,
            User.username
        )
        .select_from(ArticleComment)
        .join(User, ArticleComment.user_id==User.id)
        .where(ArticleComment.article_id==article_id)
        .order_by(ArticleComment.created_at.desc())
    )
    async with session.begin() as conn:
        result = (await conn.execute(query)).all()
    return [
        {
            "id": comment.id,
            "username": comment.username,
            "message": comment.message,
            "created_at": comment.created_at
        } for comment in result
    ]


async def delete_my_article_comment(
        session: async_sessionmaker[AsyncSession],
        article_comment_id: ArticleCommentId,
        user_id: UserId
) -> None:
    query = sa.delete(ArticleComment).where(
        sa.and_(
            ArticleComment.id==article_comment_id,
            ArticleComment.user_id==user_id
        )
    ).returning(ArticleComment.id)
    try:
        async with session.begin() as conn:
            result: ArticleCommentId | None = await conn.scalar(query)
            if result is None:
                raise CommentNotOwner
    except CommentNotOwner as ex:
        logger.warning(ex)
        raise CommentNotOwner
    
