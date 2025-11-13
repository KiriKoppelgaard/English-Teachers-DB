"""
Test script to verify all functionality works correctly.
"""
from TeacherLibrary.data.database import SessionLocal, init_db
from TeacherLibrary.models.crud import book_crud, dvd_crud
from TeacherLibrary.data.semantic_search import semantic_search, semantic_search_dvd

# Initialize database
init_db()

def test_books():
    """Test book CRUD operations."""
    print("\n=== Testing Books ===")
    db = SessionLocal()

    try:
        # Create a book
        book_data = {
            "title": "To Kill a Mockingbird",
            "author": "Harper Lee",
            "theme": "Justice and morality",
            "geographical_area": "USA",
            "publication_year": 1960,
            "genre": "Fiction",
            "subgenre": "Southern Gothic",
            "material_type": "Hardcover",
            "notes": "Classic American novel",
            "description": "A gripping tale of racial injustice and childhood innocence in the American South during the 1930s."
        }
        book = book_crud.create(db, book_data)
        print(f"✅ Created book: {book.title} (ID: {book.id})")

        # Get all books
        all_books = book_crud.get_all(db)
        print(f"✅ Retrieved {len(all_books)} books")

        # Search books
        search_results = book_crud.get_all(db, search="Mockingbird")
        print(f"✅ Search found {len(search_results)} books matching 'Mockingbird'")

        # Semantic search
        books_dict = [b.to_dict() for b in all_books]
        semantic_results = semantic_search("books about justice and courage", books_dict, top_k=5)
        print(f"✅ Semantic search found {len(semantic_results)} books about justice and courage")

        # Update book
        book_crud.update(db, book.id, {"notes": "Updated: Pulitzer Prize winner"})
        updated_book = book_crud.get(db, book.id)
        print(f"✅ Updated book notes: {updated_book.notes}")

        # Delete book
        book_crud.delete(db, book.id)
        print(f"✅ Deleted book (ID: {book.id})")

        print("\n✅ All book tests passed!")

    except Exception as e:
        print(f"\n❌ Book test failed: {e}")
    finally:
        db.close()


def test_dvds():
    """Test DVD CRUD operations."""
    print("\n=== Testing DVDs ===")
    db = SessionLocal()

    try:
        # Create a DVD
        dvd_data = {
            "title": "An Inconvenient Truth",
            "director": "Davis Guggenheim",
            "theme": "Climate change",
            "geographical_area": "USA",
            "publication_year": 2006,
            "genre": "Documentary",
            "subgenre": "Environmental",
            "material_type": "DVD",
            "notes": "Academy Award winner",
            "description": "Al Gore's campaign to educate people about global warming through a comprehensive slide show."
        }
        dvd = dvd_crud.create(db, dvd_data)
        print(f"✅ Created DVD: {dvd.title} (ID: {dvd.id})")

        # Get all DVDs
        all_dvds = dvd_crud.get_all(db)
        print(f"✅ Retrieved {len(all_dvds)} DVDs")

        # Search DVDs
        search_results = dvd_crud.get_all(db, search="Truth")
        print(f"✅ Search found {len(search_results)} DVDs matching 'Truth'")

        # Semantic search
        dvds_dict = [d.to_dict() for d in all_dvds]
        semantic_results = semantic_search_dvd("documentaries about environmental issues", dvds_dict, top_k=5)
        print(f"✅ Semantic search found {len(semantic_results)} DVDs about environmental issues")

        # Update DVD
        dvd_crud.update(db, dvd.id, {"notes": "Updated: Two Academy Awards"})
        updated_dvd = dvd_crud.get(db, dvd.id)
        print(f"✅ Updated DVD notes: {updated_dvd.notes}")

        # Delete DVD
        dvd_crud.delete(db, dvd.id)
        print(f"✅ Deleted DVD (ID: {dvd.id})")

        print("\n✅ All DVD tests passed!")

    except Exception as e:
        print(f"\n❌ DVD test failed: {e}")
    finally:
        db.close()


if __name__ == "__main__":
    print("🧪 Running functionality tests...")
    test_books()
    test_dvds()
    print("\n✅ All tests completed successfully!")
