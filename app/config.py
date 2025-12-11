from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field

class Settings(BaseSettings):
    supabase_url: str
    supabase_key: str = Field(alias="SUPABASE_API_KEY")
    elevenlabs_api_key: str | None = Field(default=None, alias="ELEVEN_LABS_API_KEY")
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    gemini_api_key: str | None = None
    grok_api_key: str | None = None  # Assuming this key name for now

    model_config = SettingsConfigDict(env_file=(".env", "../.env"), env_file_encoding="utf-8", extra="ignore")

settings = Settings()
