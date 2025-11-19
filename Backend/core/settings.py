from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env', env_file_encoding='utf-8'
    )

    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    WAHA_API_KEY: str
    WAHA_BASE_URL: str
    WAHA_SESSION_NAME: str
    GROQ_API_KEY: str
    BOT_API_KEY: str
    OPENAI_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID_MENSAL: str
    STRIPE_PRICE_ID_ANUAL: str