from pydantic import SecretStr, field_validator
from enum import Enum
from pydantic_settings import BaseSettings


class BaseAppSettings(BaseSettings):
    class Config:
        env_file = ".env"
        extra = "ignore"
class AppSettings(BaseAppSettings):
    # Database connection pool settings
    # Connection pool sized for merged workload:
    # - Previous: Main DB (40+5) + Push DB (30+15) = 90 total connections
    # - Merged: Single DB (70+20) = 90 total connections (same capacity)
    pool_size: int = 70  # Increased to handle merged workload (40 main + 30 push)
    max_overflow: int = 20  # Increased accordingly (5 main + 15 push)
    pool_recycle: int = 600  # Recycle connections after 10 minutes
    pool_timeout: int = 30  # Wait up to 30 seconds for a connection
    pg_url: SecretStr
    max_page_size: int = 1000  # Maximum page size for API responses

settings = AppSettings()
