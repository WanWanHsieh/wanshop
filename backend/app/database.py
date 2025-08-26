from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./app.db"
    # 忽略 .env 中多餘的鍵（如 SECRET_KEY、CORS_ALLOW_ORIGINS），避免 ValidationError
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)


class Base(DeclarativeBase):
    pass


def init_db():
    from . import models  # noqa

    Base.metadata.create_all(bind=engine)
