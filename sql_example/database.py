from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from config import settings
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text, String, create_engine
import uuid

engine = create_engine(settings.database_url)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("gen_random_uuid()")
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(nullable=False)

Base.metadata.create_all(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False,bind=engine)

