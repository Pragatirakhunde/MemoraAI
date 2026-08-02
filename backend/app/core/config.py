from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str
    HOST: str
    PORT: int
    APP_VERSION: str
    
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str

    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    QDRANT_HOST: str
    QDRANT_PORT: int

    REDIS_HOST: str
    REDIS_PORT: int

    JWT_SECRET: str

    GOOGLE_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()