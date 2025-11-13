"""Configuration management using environment variables."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/english_teachers_library"
    )

    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL from environment."""
        return cls.DATABASE_URL
