from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MONGO_URI: str = "mongodb://localhost:27017/"
    EMAIL_USERNAME: str = "email"
    EMAIL_PASSWORD: str = "password"
    API_TOKEN: str = "token"
    EMAIL_FROM: str = "email"
    EMAIL_PROVIDER: str = "smtp2go"
    EMAIL_CONFIGS: dict = {
        "smtp2go": {"host": "mail.smtp2go.com", "port": 2525}
    }
    EXPIRE_TIME: int = 5

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()