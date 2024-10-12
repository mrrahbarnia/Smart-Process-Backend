import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import date, datetime
from decimal import Decimal
from uuid import uuid4

from src.database import Base
from src.products import types
from src.auth.models import User
from src.auth.types import UserId


class Category(Base):
    __tablename__ = "categories"
    __table_args__ = (
        sa.Index("idx_active_category", "is_active", postgresql_where=sa.text("is_active = TRUE")),
    )

    id: so.Mapped[types.CategoryId] = so.mapped_column(autoincrement=True, primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(150), unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    is_active: so.Mapped[bool] = so.mapped_column(default=True, init=False)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    parent_id: so.Mapped[types.CategoryId | None] = so.mapped_column(sa.ForeignKey(
        "categories.id", ondelete="SET NULL"
    ), index=True)


    def __repr__(self) -> str:
        return f"{self.id} {self.name}"


class Brand(Base):
    __tablename__ = "brands"
    __table_args__ = (
        sa.Index("idx_active_brands", "is_active", postgresql_where=sa.text("is_active = TRUE")),
    )

    id: so.Mapped[types.BrandId] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200), unique=True)
    slug: so.Mapped[str] = so.mapped_column(sa.String(250), index=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    is_active: so.Mapped[bool] = so.mapped_column(default=True)

    def __repr__(self) -> str:
        return f"{self.id} {self.name}"


class Product(Base):
    __tablename__ = "products"
    __table_args__ = (
        sa.CheckConstraint("stock >= 0", name="check_positive_stock"),
        sa.CheckConstraint("views >= 0", name="check_positive_views"),
        sa.CheckConstraint("price >= 0", name="check_positive_price"),
        sa.CheckConstraint("discount BETWEEN 0 AND 100", name="check_discount_percent"),
        sa.Index("idx_active_products", "is_active", postgresql_where=sa.text("is_active = TRUE"))
    )

    id: so.Mapped[types.ProductId] = so.mapped_column(primary_key=True, default=uuid4, init=False)
    serial_number: so.Mapped[types.SerialNumber] = so.mapped_column(sa.String(150), unique=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200), unique=True)
    description: so.Mapped[str] = so.mapped_column(sa.Text)
    stock: so.Mapped[int]
    price: so.Mapped[Decimal] = so.mapped_column(sa.DECIMAL(20, 3))
    discount: so.Mapped[int | None]
    expiry_discount: so.Mapped[date | None] = so.mapped_column(sa.TIMESTAMP(timezone=True))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    views: so.Mapped[int] = so.mapped_column(default=0, init=False)
    is_active: so.Mapped[bool] = so.mapped_column(default=True, init=False)

    brand_id: so.Mapped[types.BrandId | None] = so.mapped_column(sa.ForeignKey(
        f"{Brand.__tablename__}.id", ondelete="SET NULL"
    ), index=True)
    category_id: so.Mapped[types.CategoryId | None] = so.mapped_column(sa.ForeignKey(
        f"{Category.__tablename__}.id", ondelete="SET NULL"
    ), index=True)

    def __repr__(self) -> str:
        return f"{self.id} {self.name}"


class ProductImage(Base):
    __tablename__ = "productimages"

    id: so.Mapped[types.ProductImageId] = so.mapped_column(autoincrement=True, primary_key=True)
    url: so.Mapped[str] = so.mapped_column(sa.String(250))

    product_id: so.Mapped[types.ProductId] = so.mapped_column(sa.ForeignKey(
        f"{Product.__tablename__}.id", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"{self.id} {self.url}"


class Attribute(Base):
    __tablename__ = "attributes"

    name: so.Mapped[str] = so.mapped_column(sa.String(200), primary_key=True)

    def __repr__(self) -> str:
        return f"{self.name}"


class CategoryAttribute(Base):
    __tablename__ = "categoryattributes"
    __table_args__ = (
        sa.PrimaryKeyConstraint("category_id", "attribute_name"),
    )

    category_id: so.Mapped[types.CategoryId] = so.mapped_column(sa.ForeignKey(
        f"{Category.__tablename__}.id", ondelete="CASCADE"
    ), index=True)
    attribute_name: so.Mapped[str] = so.mapped_column(sa.ForeignKey(
        f"{Attribute.__tablename__}.name", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"category_id: {self.category_id}, attribute_name: {self.attribute_name}"


class AttributeValue(Base):
    __tablename__ = "attributevalues"

    id: so.Mapped[types.AttributeValueId] = so.mapped_column(autoincrement=True, primary_key=True)
    value: so.Mapped[str | None] = so.mapped_column(sa.String(200))

    attribute_name: so.Mapped[str] = so.mapped_column(sa.ForeignKey(
        f"{Attribute.__tablename__}.name", ondelete="CASCADE"
    ), index=True)
    product_id: so.Mapped[types.ProductId | None] = so.mapped_column(sa.ForeignKey(
        f"{Product.__tablename__}.id", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"attribute_name: {self.attribute_name}, product_id: {self.product_id}"


class Comment(Base):
    __tablename__ = "comments"

    id: so.Mapped[types.CommentId] = so.mapped_column(autoincrement=True, primary_key=True)
    message: so.Mapped[str] = so.mapped_column(sa.Text)
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    product_id: so.Mapped[types.ProductId] = so.mapped_column(sa.ForeignKey(
        f"{Product.__tablename__}.id", ondelete="CASCADE"
    ), index=True)
    user_id: so.Mapped[UserId] = so.mapped_column(sa.ForeignKey(
        f"{User.__tablename__}.id", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"{self.id}"

