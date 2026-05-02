import logging
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

"""
Configuration module for Knowledge Hub application.
Loads environment variables from .env file using Pydantic settings.
"""

# Configure module logger
logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    Attributes:
    client_url: Frontend application URL (for CORS)
    server_url: Backend API URL
    storage_path: Filesystem path for file storage
    groq_api_key: API key for OpenRouter/LLM service
    """

    client_url: str
    server_url: str
    storage_path: str
    groq_api_key: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    settings = Settings()
    logger.info("✓ Settings loaded successfully")
    logger.info(f"  Storage path: {settings.storage_path}")
    logger.info(f"  Client URL: {settings.client_url}")
except Exception as e:
    logger.error("✗ Failed to load settings from .env file")
    logger.error(f"  Error: {e}")
    logger.error(f"  Location: {__file__}")
    raise e
