import re
import uuid
from typing import Annotated
from datetime import datetime
from pydantic import BeforeValidator, StringConstraints, BaseModel, EmailStr, field_validator


def normalize_full_name(value: str) -> str:
    if not isinstance(value, str):
        return value

    return re.sub(r"\s+", " ", value).strip().lower()


Name = Annotated[
    str,
    BeforeValidator(normalize_full_name),
    StringConstraints(
        min_length=2,
        max_length=50,
        pattern=r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$",
    ),
]

Password = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d\s])\S+$",
    ),
]

class UserCreate(BaseModel):
    full_name: Name
    email: EmailStr
    password: Password
    phone: str | None = None

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        if isinstance(value, str):
            return value.strip().lower()
        return value

class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}  # Enables SQLAlchemy → Pydantic conversion