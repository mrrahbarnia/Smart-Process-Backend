import sqlalchemy as sa
import sqlalchemy.orm as so

from decimal import Decimal
from datetime import datetime

from src.database import Base
from src.sales import types
from src.auth.types import UserId
from src.auth.models import User
from src.products.models import Product
from src.products.types import ProductId


class Sale(Base):
    __tablename__ = "sales"
    __table_args__ = (
        sa.CheckConstraint("total_quantity >= 1", name="total_quantity_check"),
    )

    id: so.Mapped[types.SaleId] = so.mapped_column(autoincrement=True, primary_key=True)
    total_quantity: so.Mapped[int]
    total_price: so.Mapped[Decimal] = so.mapped_column(sa.DECIMAL(20, 3))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    user_id: so.Mapped[UserId | None] = so.mapped_column(sa.ForeignKey(
        f"{User.__tablename__}.id", ondelete="SET NULL"
    ), index=True)

    def __repr__(self) -> str:
        return f"{self.id}"


class SaleProduct(Base):
    __tablename__ = "sale_products"
    __table_args__ = (
        sa.PrimaryKeyConstraint("sale_id", "product_id"),
    )

    sale_id: so.Mapped[types.SaleId] = so.mapped_column(sa.ForeignKey(
        f"{Sale.__tablename__}.id", ondelete=""
    ))
    product_id: so.Mapped[ProductId] = so.mapped_column(sa.ForeignKey(
        f"{Product.__tablename__}.id", ondelete=""
    ))

    def __repr__(self) -> str:
        return f"sale_id: {self.sale_id}, product_id: {self.product_id}"
