from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Enterprise Memory Engine"
    APP_VERSION: str = "1.0.0"

    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    POSTGRES_HOST: str
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    QDRANT_URL: str = ""
    QDRANT_API_KEY: str = ""

    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    EMBEDDING_MODEL: str = "BAAI/bge-m3"

    REDIS_HOST: str
    REDIS_PORT: int = 6379
    PROMETHEUS_ENABLED: bool = True
    CELERY_METRICS_PORT: int = 9808

    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60

    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    REDIS_URL: str = "redis://localhost:6379/0"
    SYNC_INTERVAL_SECONDS: int = 900

    CODEMIND_QDRANT_COLLECTION: str = "codemind_code_chunks"
    CODEMIND_MAX_FILE_SIZE_MB: int = 5
    GITHUB_WEBHOOK_SECRET: str = ""
    GITHUB_TOKEN: str = ""
    CODEMIND_GIT_HISTORY_DEPTH: int = 100
    CODEMIND_GIT_HISTORY_LIMIT: int = 100

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def postgres_url(self) -> str:
        return (
            f"postgresql+psycopg2://"
            f"{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}"
            f"/{self.POSTGRES_DB}"
        )


settings = Settings()