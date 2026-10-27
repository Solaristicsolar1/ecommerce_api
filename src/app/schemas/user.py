import re
import uuid
from typing import Annotated
from datetime import datetime

from pydantic import (
    BeforeValidator,
    StringConstraints,
    BaseModel,
    EmailStr,
)


# ---------------------------------------------------------------
# REUSABLE TYPES
# Each type bundles "clean up" + "check" rules in one place, so any
# schema can use it by just writing e.g. `email: Email`.
# ---------------------------------------------------------------

# Password rules: 8-128 characters, with at least one lowercase letter,
# one uppercase letter, one digit, one special character, and no spaces.
# The (?=...) parts are "lookaheads": each one demands that something
# exists somewhere in the text. Pydantic's default regex engine can't
# handle them, so any model using this type needs
# model_config = {"regex_engine": "python-re"}.
StrongPassword = Annotated[
    str,
    StringConstraints(
        min_length=8,
        max_length=128,
        pattern=r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[^A-Za-z\d\s])\S+$",
    ),
]


def normalize_full_name(value: str) -> str:
    # If it's not a string (e.g. None or a number), leave it alone and let
    # the later checks report the proper error.
    if not isinstance(value, str):
        return value

    # Collapse repeated whitespace into one space, trim the ends,
    # and lowercase: "  Jane   DOE " -> "jane doe"
    return re.sub(r"\s+", " ", value).strip().lower()


# Name: cleaned FIRST (BeforeValidator), then checked against the rules:
# 2-50 characters, letters only, with single spaces, apostrophes or
# hyphens allowed between words (e.g. "mary-jane o'brien").
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
    # Same idea: only touch strings, pass everything else through.
    if isinstance(value, str):
        # Trim spaces and lowercase: " Jane@Example.com " -> "jane@example.com"
        return value.strip().lower()
    return value


# Email: cleaned FIRST, then validated by EmailStr (which checks the
# format). Cleaning first matters, because stray spaces would make
# EmailStr reject an otherwise valid address.
Email = Annotated[
    EmailStr,
    BeforeValidator(normalize_email),
]

Phone = Annotated[
    str,
    StringConstraints(min_length=7, max_length=20),
]

# ---------------------------------------------------------------
# SCHEMAS
# These describe the shape of data going into and out of the API.
# ---------------------------------------------------------------

# Data the client sends when signing up.
class UserCreate(BaseModel):
    # Required because StrongPassword uses lookaheads (see above).
    model_config = {"regex_engine": "python-re"}

    full_name: Name
    email: Email
    password: StrongPassword
    phone: Phone | None = None  # optional


# Data the API sends back. Note: no password field, so it can never leak.
class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    email_verified: bool
    created_at: datetime

    # Lets Pydantic read data straight from a database object (the
    # SQLAlchemy User model) instead of requiring a dictionary.
    model_config = {"from_attributes": True}


# Data the client sends when editing a profile (PATCH).
# Every field is optional, so the client can send only what changed.
# Name and Email give updates the same cleanup and rules as sign-up.
class UserUpdate(BaseModel):
    full_name: Name | None = None
    email: Email | None = None
    phone: Phone | None = None