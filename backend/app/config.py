import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    API_TITLE: str = "项目经费预算报价系统 API"
    API_VERSION: str = "1.0.0"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./data/quotation.db"

    class Config:
        env_file = ".env"

settings = Settings()
