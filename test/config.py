from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # We define the variables we expect to find in the .env file
    environment: str = "development"
    database_url: str

    # This tells Pydantic: "Go look in the .env file for these values"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

# We create ONE instance of this settings object to use globally
settings = Settings()

if __name__ == "__main__":
    print(f"✅ DB URL: {settings.database_url}")
    print(f"✅ Env: {settings.environment}")