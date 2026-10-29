from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    # We define the variables we expect to find in the .env file
    environment: str = "development"
    database_url: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    # This tells Pydantic: "Go look in the .env file for these values"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

# Use lru_cache to avoid reading .env on every request


@lru_cache()
def get_settings() -> Settings:
    return Settings()
