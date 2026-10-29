import jwt
from datetime import datetime, timedelta, timezone
from app.config import get_settings

settings = get_settings()

# to calculate the expiration time of the token, we add the current time to the expiration time in minutes from the settings
expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)