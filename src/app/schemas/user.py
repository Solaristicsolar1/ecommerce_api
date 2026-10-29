import re
import uuid
import phonenumbers

from phonenumbers import PhoneNumberFormat
from app.models.user import UserRole
from datetime import datetime
from typing import Annotated

from pydantic import (
    BaseModel,
    BeforeValidator,
    StringConstraints,
    EmailStr,
    ConfigDict,
)



# --------------------------------------------------
# REUSABLE TYPES
# --------------------------------------------------

StrongPassword = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d\s])\S+$",
    ),
]


def normalize_full_name(value: str) -> str:
    if not isinstance(value, str):
        return value

    # Remove extra spaces and preserve the person's letter case.
    return re.sub(r"\s+", " ", value).strip()


Name = Annotated[
    str,
    BeforeValidator(normalize_full_name),
    StringConstraints(
        min_length=2,
        max_length=50,
        pattern=r"^[^\W\d_]+(?:[ '-][^\W\d_]+)*$",
    ),
]


def normalize_email(value):
    if isinstance(value, str):
        return value.strip().lower()
    return value


Email = Annotated[
    EmailStr,
    BeforeValidator(normalize_email),
]


def validate_nigerian_phone(value: str) -> str:
    if not isinstance(value, str):
        raise ValueError("Phone number must be a string")

    try:
        number = phonenumbers.parse(value, "NG")
    except phonenumbers.NumberParseException:
        raise ValueError("Invalid Nigerian phone number")

    if not phonenumbers.is_valid_number_for_region(number, "NG"):
        raise ValueError("Enter a valid Nigerian phone number")

    return phonenumbers.format_number(
        number, PhoneNumberFormat.E164
    )

Phone = Annotated[
    str,
    BeforeValidator(validate_nigerian_phone),
]


# --------------------------------------------------
# CUSTOMER REGISTRATION
# --------------------------------------------------

class CustomerRegister(BaseModel):
    model_config = ConfigDict(regex_engine="python-re")

    full_name: Name
    email: Email
    password: StrongPassword
    phone: Phone


# --------------------------------------------------
# USER RESPONSE
# --------------------------------------------------

class UserResponse(BaseModel):
    id: uuid.UUID
    full_name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool
    email_verified: bool
    phone_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --------------------------------------------------
# UPDATE OWN PROFILE
# --------------------------------------------------

class UserUpdate(BaseModel):
    model_config = ConfigDict(regex_engine="python-re")

    full_name: Name | None = None
    phone: Phone | None = None


# --------------------------------------------------
# CURRENT USER RESPONSE
# --------------------------------------------------

class UserMeResponse(UserResponse):
    pass
