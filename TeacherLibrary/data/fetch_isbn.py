"""
ISBN data fetching module.

This module provides functions to fetch book metadata from ISBN using Google Books API.
Follows data science best practices: minimal code, clear error handling, single responsibility.
"""
from typing import Dict, Optional

import requests


def fetch_book_by_isbn(isbn: str) -> Optional[Dict[str, str]]:
    """
    Fetch book metadata from Google Books API using ISBN.

    Args:
        isbn: International Standard Book Number (10 or 13 digits)

    Returns:
        Dictionary with book data or None if not found
        Keys: title, author, publisher, publication_year, description, isbn

    Example:
        >>> data = fetch_book_by_isbn("9780061120084")
        >>> print(data['title'])
        'To Kill a Mockingbird'
    """
    if not isbn or not isbn.replace("-", "").isdigit():
        return None

    # Clean ISBN (remove hyphens and spaces)
    clean_isbn = isbn.replace("-", "").replace(" ", "")

    try:
        # Google Books API - free, no API key required
        url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{clean_isbn}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("totalItems", 0) == 0:
            return None

        # Extract book information
        book_info = data["items"][0]["volumeInfo"]

        # Parse authors (may be a list)
        authors = book_info.get("authors", [])
        author = ", ".join(authors) if authors else ""

        # Extract publication year from publishedDate (format: YYYY-MM-DD or YYYY)
        published_date = book_info.get("publishedDate", "")
        publication_year = None
        if published_date:
            try:
                publication_year = int(published_date[:4])
            except (ValueError, IndexError):
                pass

        return {
            "title": book_info.get("title", ""),
            "author": author,
            "publisher": book_info.get("publisher", ""),
            "publication_year": publication_year,
            "description": book_info.get("description", ""),
            "isbn": clean_isbn,
            "categories": ", ".join(book_info.get("categories", [])),
        }

    except (requests.RequestException, KeyError, ValueError):
        # Failed to fetch or parse data
        return None
