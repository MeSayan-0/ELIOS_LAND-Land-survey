from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "ELIOS-LAND API"
    app_env: str = "development"
    database_url: str
    storage_root: str = "./storage"
    max_upload_size_mb: int = 2048

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
