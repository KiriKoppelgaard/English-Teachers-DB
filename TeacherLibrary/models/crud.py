"""Generic CRUD operations."""
import logging
from typing import Any, Dict, List, Optional, Type, TypeVar

from sqlalchemy import or_
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from TeacherLibrary.data.database import Base
from TeacherLibrary.models.schemas import Book, DVD

logger = logging.getLogger(__name__)

ModelType = TypeVar("ModelType", bound=Base)


class CRUDBase:
    """Generic CRUD operations."""

    def __init__(self, model: Type[ModelType]):
        """Initialize with model."""
        self.model = model

    def create(self, db: Session, obj_data: Dict[str, Any]) -> ModelType:
        """Create a new record."""
        try:
            db_obj = self.model(**obj_data)
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error creating {self.model.__name__}: {e}")
            raise ValueError(f"Failed to create {self.model.__name__}: {str(e)}")

    def get(self, db: Session, id: int) -> Optional[ModelType]:
        """Get record by ID."""
        return db.query(self.model).filter(self.model.id == id).first()

    def get_all(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 1000,
        sort_by: Optional[str] = None,
        search: Optional[str] = None,
        **filters,
    ) -> List[ModelType]:
        """Get all records with optional filtering and sorting."""
        query = db.query(self.model)

        # Apply search filter
        if search:
            search_cols = [
                col for col in self.model.__table__.columns if col.type.python_type == str
            ]
            query = query.filter(
                or_(*[col.ilike(f"%{search}%") for col in search_cols])
            )

        # Apply field filters
        for key, value in filters.items():
            if value is not None and hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)

        # Apply sorting
        if sort_by and hasattr(self.model, sort_by):
            query = query.order_by(getattr(self.model, sort_by))

        return query.offset(skip).limit(limit).all()

    def update(self, db: Session, id: int, obj_data: Dict[str, Any]) -> Optional[ModelType]:
        """Update a record."""
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with id {id} not found")
                return None

            for key, value in obj_data.items():
                setattr(db_obj, key, value)
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error updating {self.model.__name__} {id}: {e}")
            raise ValueError(f"Failed to update {self.model.__name__}: {str(e)}")

    def delete(self, db: Session, id: int) -> bool:
        """Delete a record."""
        try:
            db_obj = self.get(db, id)
            if not db_obj:
                logger.warning(f"{self.model.__name__} with id {id} not found")
                return False

            db.delete(db_obj)
            db.commit()
            return True
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Error deleting {self.model.__name__} {id}: {e}")
            raise ValueError(f"Failed to delete {self.model.__name__}: {str(e)}")


# Create instances for each model
book_crud = CRUDBase(Book)
dvd_crud = CRUDBase(DVD)
