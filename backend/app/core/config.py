from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # ==========================
    # Application
    # ==========================
    PROJECT_NAME: str = "CampusMind AI"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"

    DEBUG: bool = True

    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # ==========================
    # Database
    # ==========================
    DATABASE_URL: str

    # ==========================
    # Authentication
    # ==========================
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    ADMIN_EMAIL: str | None = None

    # ==========================
    # Gemini AI
    # ==========================
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-2.5-flash"

    # ==========================
    # Uploads
    # ==========================
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 100

    # ==========================
    # Pydantic Settings
    # ==========================
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()