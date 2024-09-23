import sqlalchemy as sa
import sqlalchemy.orm as so

from decimal import Decimal
from datetime import datetime

from src.database import Base
from src.cart import types
from src.auth.models import User
from src.auth.types import UserId
from src.products.models import Product
from src.products.types import ProductId


class Cart(Base):
    __tablename__ = "carts"

    id: so.Mapped[types.CartId] = so.mapped_column(primary_key=True, autoincrement=True)
    total_quantity: so.Mapped[int | None]
    total_price: so.Mapped[Decimal | None] = so.mapped_column(sa.DECIMAL(20, 3))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    modified_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), onupdate= sa.func.now()
    )

    user_id: so.Mapped[UserId] = so.mapped_column(sa.ForeignKey(
        f"{User.__tablename__}.id", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"{self.id}"


class CartProduct(Base):
    __tablename__ = "cart_products"
    __table_args__ = (
        sa.PrimaryKeyConstraint("cart_id", "product_id"),
    )

    cart_id: so.Mapped[types.CartId] = so.mapped_column(sa.ForeignKey(
        f"{Cart.__tablename__}.id", ondelete="CASCADE"
    ), index=True)
    product_id: so.Mapped[ProductId] = so.mapped_column(sa.ForeignKey(
        f"{Product.__tablename__}.id", ondelete="CASCADE"
    ), index=True)

    def __repr__(self) -> str:
        return f"cart_id: {self.cart_id}, product_id: {self.product_id}"