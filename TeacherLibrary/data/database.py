"""Database session management."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from TeacherLibrary.config import Config

engine = create_engine(Config.get_database_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    # Import models to register them with Base.metadata
    from TeacherLibrary.models import schemas  # noqa: F401
    Base.metadata.create_all(bind=engine)
