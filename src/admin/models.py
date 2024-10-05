import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime

from src.database import Base
from src.admin.types import GuarantyId, GuarantySerial
from src.products.types import SerialNumber


class Guaranty(Base):
    __tablename__ = "guaranties"
    id: so.Mapped[GuarantyId] = so.mapped_column(primary_key=True, autoincrement=True)
    product_serial_number: so.Mapped[SerialNumber] = so.mapped_column(sa.String(150))
    guaranty_serial: so.Mapped[GuarantySerial] = so.mapped_column(sa.String(200), index=True) # unique=True instead of index=True in production
    product_name: so.Mapped[str] = so.mapped_column(sa.String(200))
    date_of_document: so.Mapped[str] = so.mapped_column(sa.String(100))
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"{self.id}"
