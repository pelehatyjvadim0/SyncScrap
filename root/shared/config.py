from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class DB_Settings(BaseSettings):
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    PORT: int = 5432
    NAME: str = "user_db"
    HOST: str = "localhost"

    @property
    def DATABASE_URL(self):
        password = quote_plus(self.PASSWORD)
        return f"postgresql+asyncpg://{self.USER}:{password}@{self.HOST}:{self.PORT}/{self.NAME}"

    model_config = SettingsConfigDict(env_prefix="DB_", env_file=".env", extra="ignore")


class RabbitMq_Settings(BaseSettings):
    USER: str = "guest"
    PASS: str = "guest"
    HOST: str = "localhost"
    PORT: int = 5672

    @property
    def RABBITMQ_URL(self):
        password = quote_plus(self.PASS)
        return f"amqp://{self.USER}:{password}@{self.HOST}:{self.PORT}/"

    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_", env_file=".env", extra="ignore"
    )


class RedisSettings(BaseSettings):
    USERNAME: str = "redis"
    PASSWORD: str = "redis"
    HOST: str = "localhost"
    PORT: int = 6379

    @property
    def REDIS_URL(self):
        password = quote_plus(self.PASSWORD)
        return f"redis://{self.USERNAME}:{password}@{self.HOST}:{self.PORT}/0"

    model_config = SettingsConfigDict(
        env_prefix="REDIS_", env_file=".env", extra="ignore"
    )


class DownloaderSettings(BaseSettings):
    MAX_RETRIES: int = 3
    BASE_DELAY_SECONDS: float = 0.5
    HTML_EXPIRE_SECONDS: int = 600

    model_config = SettingsConfigDict(
        env_prefix="DOWNLOADER_", env_file=".env", extra="ignore"
    )


class Settings(BaseSettings):
    db: DB_Settings = DB_Settings()
    rabbit: RabbitMq_Settings = RabbitMq_Settings()
    redis: RedisSettings = RedisSettings()
    downloader: DownloaderSettings = DownloaderSettings()


settings = Settings()
