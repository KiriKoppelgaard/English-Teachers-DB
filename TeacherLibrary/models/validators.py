"""Pydantic validators for data validation."""
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class BookSchema(BaseModel):
    """Book validation schema."""

    book_number: Optional[int] = None
    title: str = Field(..., min_length=1, max_length=255)
    author: Optional[str] = Field(None, max_length=255)
    location: Optional[str] = Field(None, max_length=100)
    borrowed_count: int = Field(default=0, ge=0)
    total_count: int = Field(default=0, ge=0)
    theme: Optional[str] = Field(None, max_length=255)
    geographical_area: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
    genre: Optional[str] = Field(None, max_length=100)
    subgenre: Optional[str] = Field(None, max_length=100)
    material_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    description: Optional[str] = None

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v):
        """Ensure title is not empty."""
        if v and v.strip() == "":
            raise ValueError("Title cannot be empty")
        return v.strip() if v else v

    @field_validator("author")
    @classmethod
    def author_not_empty(cls, v):
        """Ensure author is not empty if provided."""
        if v is not None and v.strip() == "":
            return None
        return v.strip() if v else None

    class Config:
        from_attributes = True


class DVDSchema(BaseModel):
    """DVD validation schema."""

    title: str = Field(..., min_length=1, max_length=255)
    director: str = Field(..., min_length=1, max_length=255)
    theme: Optional[str] = Field(None, max_length=255)
    geographical_area: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
    genre: Optional[str] = Field(None, max_length=100)
    subgenre: Optional[str] = Field(None, max_length=100)
    material_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    description: Optional[str] = None

    @field_validator("title", "director")
    @classmethod
    def not_empty(cls, v):
        """Ensure required fields are not empty."""
        if v and v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v.strip() if v else v

    class Config:
        from_attributes = True
