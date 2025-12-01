"""Database models for books and DVDs."""
from sqlalchemy import Column, Integer, String, Text

from TeacherLibrary.data.database import Base


class Book(Base):
    """Book model."""

    __tablename__ = "books"

    id = Column(Integer, primary_key=True, index=True)
    book_number = Column(Integer, unique=True, index=True, nullable=True)
    title = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=True, index=True)
    location = Column(String(100), nullable=True)
    borrowed_count = Column(Integer, default=0, nullable=False)
    total_count = Column(Integer, default=0, nullable=False)
    theme = Column(String(255), index=True)
    geographical_area = Column(String(255), index=True)
    publication_year = Column(Integer, index=True)
    genre = Column(String(100), index=True)
    subgenre = Column(String(100), index=True)
    material_type = Column(String(100), index=True)
    notes = Column(Text)
    description = Column(Text)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "book_number": self.book_number,
            "title": self.title,
            "author": self.author,
            "location": self.location,
            "borrowed_count": self.borrowed_count,
            "total_count": self.total_count,
            "theme": self.theme,
            "geographical_area": self.geographical_area,
            "publication_year": self.publication_year,
            "genre": self.genre,
            "subgenre": self.subgenre,
            "material_type": self.material_type,
            "notes": self.notes,
            "description": self.description,
        }


class DVD(Base):
    """DVD and Reference Disc model."""

    __tablename__ = "dvds"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    director = Column(String(255), nullable=False, index=True)
    theme = Column(String(255), index=True)
    geographical_area = Column(String(255), index=True)
    publication_year = Column(Integer, index=True)
    genre = Column(String(100), index=True)
    subgenre = Column(String(100), index=True)
    material_type = Column(String(100), index=True)
    notes = Column(Text)
    description = Column(Text)

    def to_dict(self):
        """Convert model to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "director": self.director,
            "theme": self.theme,
            "geographical_area": self.geographical_area,
            "publication_year": self.publication_year,
            "genre": self.genre,
            "subgenre": self.subgenre,
            "material_type": self.material_type,
            "notes": self.notes,
            "description": self.description,
        }
