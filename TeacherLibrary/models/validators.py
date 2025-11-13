"""Pydantic validators for data validation."""
from typing import Optional
from pydantic import BaseModel, Field, validator


class BookSchema(BaseModel):
    """Book validation schema."""

    title: str = Field(..., min_length=1, max_length=255)
    author: str = Field(..., min_length=1, max_length=255)
    theme: Optional[str] = Field(None, max_length=255)
    geographical_area: Optional[str] = Field(None, max_length=255)
    publication_year: Optional[int] = Field(None, ge=1000, le=9999)
    genre: Optional[str] = Field(None, max_length=100)
    subgenre: Optional[str] = Field(None, max_length=100)
    material_type: Optional[str] = Field(None, max_length=100)
    notes: Optional[str] = None
    description: Optional[str] = None

    @validator("title", "author")
    def not_empty(cls, v):
        """Ensure required fields are not empty."""
        if v and v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v.strip() if v else v

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

    @validator("title", "director")
    def not_empty(cls, v):
        """Ensure required fields are not empty."""
        if v and v.strip() == "":
            raise ValueError("Field cannot be empty")
        return v.strip() if v else v

    class Config:
        from_attributes = True
