import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Configurations
    APP_NAME: str = "AI Caption Studio"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # Storage Configurations
    UPLOAD_DIR: str = "backend/uploads"
    OUTPUT_DIR: str = "backend/outputs"
    TEMP_DIR: str = "backend/temp"
    AUDIO_FOLDER: str = "backend/temp/audio"

    # Upload Configurations
    # Default: 2 GB in bytes (2 * 1024 * 1024 * 1024)
    MAX_UPLOAD_SIZE: int = 2147483648
    ALLOWED_EXTENSIONS: List[str] = [".mp4", ".mov", ".avi", ".mkv", ".webm"]

    # Database Configurations
    DATABASE_URL: str = "sqlite:///./sql_app.db"

    # Audio Extraction Configurations
    FFMPEG_PATH: str = "ffmpeg"
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_CHANNELS: int = 1

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

# Ensure directories exist
for directory in [
    settings.UPLOAD_DIR,
    settings.OUTPUT_DIR,
    settings.TEMP_DIR,
    settings.AUDIO_FOLDER,
]:
    os.makedirs(directory, exist_ok=True)
