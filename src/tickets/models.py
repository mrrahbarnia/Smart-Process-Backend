import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime

from src.database import Base
from src.tickets.types import TicketId
from src.products.types import SerialNumber
from src.auth.types import PhoneNumber


class Ticket(Base):
    __tablename__ = "tickets"
    __table_args__ = (
        sa.CheckConstraint("guaranty_rating BETWEEN 1 AND 5", name="check_guaranty_rating"),
        sa.CheckConstraint("repairs_rating BETWEEN 1 AND 5", name="check_repairs_rating"),
        sa.CheckConstraint("notification_rating BETWEEN 1 AND 5", name="check_notification_rating"),
        sa.CheckConstraint("services_rating BETWEEN 1 AND 5", name="check_services_rating"),
        sa.CheckConstraint("smart_process_rating BETWEEN 1 AND 5", name="check_smart_process_rating"),
        sa.CheckConstraint("CHAR_LENGTH(phone_number) = 11", name="check_phone_length")
    )

    id: so.Mapped[TicketId] = so.mapped_column(primary_key=True, autoincrement=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(200))
    product_serial: so.Mapped[SerialNumber | None] = so.mapped_column(sa.String(150))
    phone_number: so.Mapped[PhoneNumber | None]
    guaranty_rating: so.Mapped[int]
    repairs_rating: so.Mapped[int]
    notification_rating: so.Mapped[int]
    personal_behavior_rating: so.Mapped[int]
    services_rating: so.Mapped[int]
    smart_process_rating: so.Mapped[int]
    criticism: so.Mapped[str] = so.mapped_column(sa.Text)
    call_request: so.Mapped[bool]
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )

    def __repr__(self) -> str:
        return f"{self.id}"



