"""Database session management."""
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from TeacherLibrary.config import Config

logger = logging.getLogger(__name__)

# Create engine with connection pooling
engine = create_engine(
    Config.get_database_url(),
    pool_size=5,              # Number of connections to maintain
    max_overflow=10,          # Max connections beyond pool_size
    pool_pre_ping=True,       # Verify connections before using
    pool_recycle=3600,        # Recycle connections after 1 hour
    echo=False                # Set to True for SQL query logging
)

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
