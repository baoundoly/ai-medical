from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:pass@localhost/ai_medical"
    SECRET_KEY: str = "change-this-to-a-strong-secret-key-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    MFA_ISSUER: str = "AI Medical"
    WHISPER_MODEL: str = "base"
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:8080"]
    APP_NAME: str = "AI Clinical Assistant Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    MAX_UPLOAD_SIZE_MB: int = 50
    AUDIO_STORAGE_PATH: str = "uploads/audio"
    LAB_REPORT_STORAGE_PATH: str = "uploads/lab_reports"
    LOW_STOCK_THRESHOLD: int = 10
    EXPIRY_WARNING_DAYS: int = 30

    class Config:
        env_file = ".env"


settings = Settings()
