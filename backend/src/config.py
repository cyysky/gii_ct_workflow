"""
Configuration settings for ED CT Brain Workflow System
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""

    # Database
    DATABASE_URL: str = "postgresql://ct_workflow:ct_secure_2026@localhost:5432/ct_brain_workflow"

    # Redis
    REDIS_URL: str = "redis://localhost:6379"

    # JWT Authentication
    JWT_SECRET: str = "ct_workflow_jwt_secret_key_2026_hospital_shah_alam"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 1440  # 24 hours

    # LLM Configuration
    LLM_BASE_URL: str = "http://60.51.17.97:9999"
    LLM_API_KEY: str = "sk-xtwb5apIbuB5AIe7jJGEbA"
    LLM_MODEL: str = "qwen3.5-397b-a17b-fp8-instruct"
    EMBEDDING_MODEL: str = "qwen3-vl-embedding-8b"

    # Application
    APP_NAME: str = "ED CT Brain Workflow System"
    DEBUG: bool = False
    API_V1_PREFIX: str = "/api/v1"

    # CORS
    CORS_ORIGINS: list = ["*"]

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()