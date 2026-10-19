import uuid
from datetime import datetime
from sqlalchemy import Boolean, DateTime, String, text, func
from sqlalchemy import Uuid
from sqlalchemy.orm import Mapped, mapped_column
from app.database import Base


class User(Base):
    __tablename__ = "users"

    # OWNER: DB → Postgres generates the UUID at insert
    id: Mapped[uuid.UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True, server_default=text("gen_random_uuid()"))

    # Business data — app supplies
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20), nullable=True)

    # OWNER: DB → initial value true, app may flip later
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("true"))

    # OWNER: DB → initial value false, app flips to true after verification
    email_verified: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text("false"))

    # OWNER: DB → now() at insert
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # OWNER: DB → now() at insert, trigger bumps on update
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())