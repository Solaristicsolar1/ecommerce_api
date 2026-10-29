from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

PASSWORD_RULES_MESSAGE = (
    "Password must include an uppercase letter, a lowercase letter, "
    "a digit, a special character, and no spaces."
)

def friendly_message(err: dict) -> str:
    field = err["loc"][-1]

    if field == "password":
        if err["type"] == "string_pattern_mismatch":
            return PASSWORD_RULES_MESSAGE
        if err["type"] == "string_too_short":
            return "Password must be at least 8 characters long."
        if err["type"] == "string_too_long":
            return "Password must be at most 128 characters long."

    # Remove Pydantic's "Value error, " prefix from our own messages
    return err["msg"].removeprefix("Value error, ")

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = [
        {
            "field": ".".join(str(part) for part in err["loc"] if part != "body"),
            "message": friendly_message(err),
        }
        for err in exc.errors()
    ]
    return JSONResponse(status_code=422, content={"detail": errors})