import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App Configurations
    APP_NAME: str = "AI Caption Studio"
    API_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    SECRET_KEY: str = "secret-super-key-ai-caption-studio-2026-production-ready"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Storage Configurations
    UPLOAD_DIR: str = "backend/uploads"
    OUTPUT_DIR: str = "backend/outputs"
    TEMP_DIR: str = "backend/temp"
    AUDIO_FOLDER: str = "backend/temp/audio"
    SUBTITLES_OUTPUT_DIR: str = "backend/outputs/subtitles"
    STYLES_DIR: str = "backend/app/styles"

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

    # Faster-Whisper Configurations
    WHISPER_MODEL: str = "small"
    DEVICE: str = "cpu"
    COMPUTE_TYPE: str = "int8"

    # WhisperX Alignment Configurations
    ALIGNMENT_DEVICE: str = "cpu"
    ALIGNMENT_BATCH_SIZE: int = 16

    # Subtitle Generation Configurations
    MAX_WORDS_PER_LINE: int = 5
    MAX_LINES: int = 2
    READING_SPEED: int = 18
    DEFAULT_SUBTITLE_FORMAT: str = "srt"

    # Caption Style Engine Configurations
    DEFAULT_STYLE: str = "default"
    DEFAULT_FONT: str = "Arial"
    DEFAULT_FONT_SIZE: int = 24

    # Caption Animation Engine Configurations
    DEFAULT_ANIMATION: str = "word_highlight"
    DEFAULT_DURATION: float = 0.3
    DEFAULT_HIGHLIGHT_COLOR: str = "#FFFF00"

    # Video Rendering Configurations
    DEFAULT_RENDER_CODEC: str = "h264"
    DEFAULT_CRF: int = 18
    DEFAULT_PRESET: str = "medium"
    DEFAULT_THREADS: int = 4
    RENDERED_OUTPUT_DIR: str = "backend/outputs/rendered"

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
    settings.SUBTITLES_OUTPUT_DIR,
    settings.STYLES_DIR,
    os.path.join(settings.STYLES_DIR, "custom"),
    settings.RENDERED_OUTPUT_DIR
]:
    os.makedirs(directory, exist_ok=True)
