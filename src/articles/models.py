import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime
from uuid import uuid4

from src.database import Base
from src.articles import types
from src.auth.models import User
from src.auth.types import UserId

class Article(Base):
    __tablename__ = "articles"

    id: so.Mapped[types.ArticleId] = so.mapped_column(
        primary_key=True, default=uuid4, init=False
    )
    title: so.Mapped[str] = so.mapped_column(sa.String(200))
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    views: so.Mapped[int] = so.mapped_column(default=0)

    def __repr__(self) -> str:
        return f"{self.id}"
    

class ArticleImage(Base):
    id: so.Mapped[types.ArticleImageId] = so.mapped_column(
        primary_key=True, autoincrement=True
    )
    url: so.Mapped[str] = so.mapped_column(sa.String(250))

    article_id: so.Mapped[types.ArticleId] = so.mapped_column(
        sa.ForeignKey(f"{Article.__tablename__}.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"{self.id}"
    

class Tag(Base):
    __tablename__ = "tags"
    id: so.Mapped[types.TagId] = so.mapped_column(
        primary_key=True, autoincrement=True
    )
    name: so.Mapped[str] =  so.mapped_column(sa.String(200))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"{self.id}"


class ArticleTag(Base):
    __tablename__ = "article_tags"
    __table_args__ = (
        sa.PrimaryKeyConstraint("article_id", "tag_id"),
    )

    article_id: so.Mapped[types.ArticleId] = so.mapped_column(
        sa.ForeignKey(f"{Article.__tablename__}.id", ondelete="CASCADE")
    )
    tag_id: so.Mapped[types.TagId] = so.mapped_column(
        sa.ForeignKey(f"{Tag.__tablename__}.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"article_id: {self.article_id}, tag_id: {self.tag_id}"


class Rating(Base):
    __tablename__ = "ratings"
    __table_args__ = (
        sa.CheckConstraint("rating BETWEEN 0 AND 5"),
    )
    id: so.Mapped[types.RatingId] = so.mapped_column(
        primary_key=True, autoincrement=True
    )
    rating: so.Mapped[int]

    user_id: so.Mapped[UserId] = so.mapped_column(
        sa.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE")
    )
    article_id: so.Mapped[types.ArticleId] = so.mapped_column(
        sa.ForeignKey(f"{Article.__tablename__}.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"{self.id}"


class ArticleComment(Base):
    __tablename__ = "article_comments"
    id: so.Mapped[types.ArticleCommentId] = so.mapped_column(
        primary_key=True, autoincrement=True
    )
    message: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    user_id: so.Mapped[UserId] = so.mapped_column(
        sa.ForeignKey(f"{User.__tablename__}.id", ondelete="CASCADE")
    )
    article_id: so.Mapped[types.ArticleId] = so.mapped_column(
        sa.ForeignKey(f"{Article.__tablename__}.id", ondelete="CASCADE")
    )

    def __repr__(self) -> str:
        return f"{self.id}"


# class Glossary(Base):
#     __tablename__ = "glossaries"
#     id: so.Mapped[types.GlossaryId] = so.mapped_column(
#         primary_key=True, autoincrement=True
#     )
#     word: so.Mapped[str] = 