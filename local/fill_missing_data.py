"""
Script to fill in missing book data by searching Google Books API.

Finds books with missing information (author, description, genre, year) and
attempts to fill them in using title search on Google Books API.
"""
import time
from typing import Optional, Dict

import requests
from sqlalchemy.orm import Session

from TeacherLibrary.data.database import SessionLocal
from TeacherLibrary.models.schemas import Book
from TeacherLibrary.models.crud import book_crud


def search_book_by_title(title: str, author: Optional[str] = None) -> Optional[Dict]:
    """
    Search for book metadata using title (and optionally author) on Google Books API.

    Args:
        title: Book title to search for
        author: Optional author name to narrow search

    Returns:
        Dictionary with book data or None if not found
    """
    try:
        # Construct search query
        query = f"intitle:{title}"
        if author:
            query += f"+inauthor:{author}"

        url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()

        if data.get("totalItems", 0) == 0:
            return None

        # Get first result
        book_info = data["items"][0]["volumeInfo"]

        # Parse authors
        authors = book_info.get("authors", [])
        author_str = ", ".join(authors) if authors else None

        # Extract publication year
        published_date = book_info.get("publishedDate", "")
        publication_year = None
        if published_date:
            try:
                publication_year = int(published_date[:4])
            except (ValueError, IndexError):
                pass

        # Get categories (genres)
        categories = book_info.get("categories", [])
        genre = categories[0] if categories else None

        return {
            "author": author_str,
            "description": book_info.get("description"),
            "genre": genre,
            "publication_year": publication_year,
        }

    except (requests.RequestException, KeyError, ValueError, IndexError):
        return None


def fill_missing_book_data(db: Session, dry_run: bool = True) -> Dict:
    """
    Find books with missing data and fill them in using Google Books API.

    Args:
        db: Database session
        dry_run: If True, only show what would be updated without saving

    Returns:
        Dictionary with statistics about the operation
    """
    stats = {
        "total_books": 0,
        "books_with_missing_data": 0,
        "books_updated": 0,
        "books_not_found": 0,
        "fields_filled": {
            "author": 0,
            "description": 0,
            "genre": 0,
            "publication_year": 0
        }
    }

    # Get all books
    all_books = db.query(Book).all()
    stats["total_books"] = len(all_books)

    print(f"Analyzing {stats['total_books']} books...")
    print("=" * 70)

    for book in all_books:
        # Check if book has missing data
        missing_fields = []
        if not book.author:
            missing_fields.append("author")
        if not book.description:
            missing_fields.append("description")
        if not book.genre:
            missing_fields.append("genre")
        if not book.publication_year:
            missing_fields.append("publication_year")

        if not missing_fields:
            continue

        stats["books_with_missing_data"] += 1

        print(f"\n[{book.book_number}] {book.title}")
        print(f"  Missing: {', '.join(missing_fields)}")

        # Try to fetch data
        print(f"  Searching Google Books...")
        fetched_data = search_book_by_title(book.title, book.author)

        if not fetched_data:
            print(f"  ✗ Not found")
            stats["books_not_found"] += 1
            continue

        # Prepare update data
        update_data = {}
        for field in missing_fields:
            if field in fetched_data and fetched_data[field]:
                update_data[field] = fetched_data[field]
                stats["fields_filled"][field] += 1
                print(f"  ✓ Found {field}: {str(fetched_data[field])[:50]}...")

        if update_data:
            if dry_run:
                print(f"  [DRY RUN] Would update: {', '.join(update_data.keys())}")
            else:
                try:
                    book_crud.update(db, book.id, update_data)
                    print(f"  ✓ Updated: {', '.join(update_data.keys())}")
                    stats["books_updated"] += 1
                except Exception as e:
                    print(f"  ✗ Error updating: {e}")

        # Rate limiting - be nice to the API
        time.sleep(1)

    return stats


def main():
    """Run the data filling script."""
    import sys

    # Check if user wants to actually update (not dry run)
    dry_run = True
    if len(sys.argv) > 1 and sys.argv[1] == "--update":
        dry_run = False
        print("⚠️  LIVE UPDATE MODE - Changes will be saved to database!")
    else:
        print("🔍 DRY RUN MODE - No changes will be saved")
        print("   Run with --update flag to actually save changes")

    print("=" * 70)
    print()

    db = SessionLocal()
    try:
        stats = fill_missing_book_data(db, dry_run=dry_run)

        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total books: {stats['total_books']}")
        print(f"Books with missing data: {stats['books_with_missing_data']}")
        print(f"Books updated: {stats['books_updated']}")
        print(f"Books not found: {stats['books_not_found']}")
        print(f"\nFields filled:")
        for field, count in stats['fields_filled'].items():
            if count > 0:
                print(f"  - {field}: {count}")

        if dry_run and stats['books_with_missing_data'] > 0:
            print(f"\n💡 Run with --update to save changes to database")

    finally:
        db.close()


if __name__ == "__main__":
    main()
