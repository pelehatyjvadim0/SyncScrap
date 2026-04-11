from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import quote_plus


class DB_Settings(BaseSettings):
    USER: str = "postgres"
    PASSWORD: str = "postgres"
    PORT: int = 5432
    NAME: str = "user_db"
    HOST: str = "localhost"
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    POOL_PRE_PING: bool = True
    POOL_RECYCLE: int = 1800

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

    CONNECTION_URL: str | None = None
    USERNAME: str = ""
    PASSWORD: str = ""
    HOST: str = "localhost"
    PORT: int = 6379

    @property
    def REDIS_URL(self) -> str:
        direct = (self.CONNECTION_URL or "").strip()
        if direct:
            return direct

        host = self.HOST
        port = self.PORT
        user = (self.USERNAME or "").strip()
        pwd_raw = self.PASSWORD or ""

        if not user and not pwd_raw:
            return f"redis://{host}:{port}/0"
        if not user and pwd_raw:
            return f"redis://:{quote_plus(pwd_raw)}@{host}:{port}/0"
        return f"redis://{quote_plus(user)}:{quote_plus(pwd_raw)}@{host}:{port}/0"

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


class SchedulerSettings(BaseSettings):
    """Периодическая отправка целей из БД в raw_urls."""

    ENABLED: bool = True
    INTERVAL_SECONDS: int = 80
    """Интервал между тиками планировщика."""
    STALE_AFTER_SECONDS: int = 3600
    """Считать URL «устаревшим», если last_scraped_at старше N секунд (UTC)."""
    MAX_URLS_PER_TICK: int = 500
    """Защита от пика: не больше URL за один тик."""
    PUBLISH_GAP_SECONDS: float = 0.02
    """Пауза между publish в Rabbit (снижает пик нагрузки на брокер)."""
    FORCE_REFRESH: bool = True
    """Передавать force_refresh в очередь (обход Redis HTML)."""

    model_config = SettingsConfigDict(
        env_prefix="SCHEDULER_", env_file=".env", extra="ignore"
    )


class Settings(BaseSettings):
    db: DB_Settings = DB_Settings()
    rabbit: RabbitMq_Settings = RabbitMq_Settings()
    redis: RedisSettings = RedisSettings()
    downloader: DownloaderSettings = DownloaderSettings()
    scheduler: SchedulerSettings = SchedulerSettings()


settings = Settings()
