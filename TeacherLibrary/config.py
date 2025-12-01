"""Configuration management using environment variables."""
import os
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5432/english_teachers_library"
    )

    @classmethod
    def setup_logging(cls, level=logging.INFO):
        """Configure structured logging for the application."""
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        return logging.getLogger(__name__)

    @classmethod
    def validate_config(cls):
        """Validate configuration on startup."""
        try:
            parsed = urlparse(cls.DATABASE_URL)
            if not parsed.scheme or not parsed.netloc:
                raise ValueError("Invalid DATABASE_URL format")
            if parsed.scheme not in ['postgresql', 'postgres']:
                raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        except Exception as e:
            raise ValueError(f"Configuration error: {e}")

    @classmethod
    def get_database_url(cls) -> str:
        """Get database URL from environment with validation."""
        cls.validate_config()
        return cls.DATABASE_URL
