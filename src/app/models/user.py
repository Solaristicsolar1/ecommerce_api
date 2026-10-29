import enum
import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, Enum, Index, String, Uuid, func, text
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class UserRole(str, enum.Enum):
    customer = "customer"
    admin = "admin"
    product_manager = "product_manager"
    fulfilment = "fulfilment"


class User(Base):
    __tablename__ = "users"
    __table_args__ = (
        Index("uq_users_email_lower", func.lower(text("email")), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()")
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), unique=True, nullable=True)

    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="user_role", values_callable=lambda e: [m.value for m in e]),
        nullable=False,
        server_default=text("'customer'"),
        index=True,
    )

    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))
    phone_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    last_login_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now()
    )