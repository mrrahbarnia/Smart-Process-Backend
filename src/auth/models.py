import sqlalchemy as sa
import sqlalchemy.orm as so

from datetime import datetime

from src.database import Base
from src.auth.types import UserId, PhoneNumber, Password, UserRole


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        sa.CheckConstraint("CHAR_LENGTH(phone_number) = 11", name="check_phone_length"),
    )

    id: so.Mapped[UserId] = so.mapped_column(primary_key=True, autoincrement=True)
    phone_number: so.Mapped[PhoneNumber] = so.mapped_column(sa.String(12), unique=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(250), unique=True)
    password: so.Mapped[Password] = so.mapped_column(sa.String(128)) # 128 for storing hash passwords
    created_at: so.Mapped[datetime] = so.mapped_column(
        sa.TIMESTAMP(timezone=True), server_default=sa.func.now()
    )
    role: so.Mapped[UserRole] = so.mapped_column(sa.Enum(UserRole), default=UserRole.USER)
    is_active: so.Mapped[bool] = so.mapped_column(default=False)

    def __repr__(self) -> str:
        return f"User {self.id} {self.phone_number}"
