from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    api_nba_key: str
    database_url: str
    api_nba_base_url: str = "https://v2.nba.api-sports.io"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
