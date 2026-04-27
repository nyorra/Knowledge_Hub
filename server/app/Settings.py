import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    client_url: str
    server_url: str

    storage_path: str

    groq_api_key: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(__file__), "../../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


try:
    settings = Settings()
except Exception as e:
    print(f"Ошибка загрузки настроек окружения. {__file__}")
    print(f"Детали: {e}")
    raise e
