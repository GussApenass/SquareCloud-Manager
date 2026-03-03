from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    BOT_TOKEN: str = Field(..., min_length=10)
    APPLICATION_ID: str = Field(..., min_length=15)
    SQUARE_CLOUD_TOKEN: str = Field(..., min_length=15)

env = Settings()