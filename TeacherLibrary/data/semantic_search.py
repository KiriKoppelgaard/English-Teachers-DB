"""
Semantic search module for finding books by meaning.

This module provides semantic search capabilities using sentence embeddings.
Follows data science best practices: caching, minimal dependencies, clean API.
"""
from typing import List, Tuple

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# Global model cache (singleton pattern for performance)
_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or create the embedding model (cached singleton).

    Uses 'all-MiniLM-L6-v2' - lightweight, fast, good for English text.
    Only ~80MB and runs on CPU efficiently.

    Returns:
        SentenceTransformer model instance
    """
    global _model
    if _model is None:
        # Lightweight model, good for books/text, fast on CPU
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model


def create_book_text(book_dict: dict) -> str:
    """
    Create searchable text representation of a book.

    Combines all relevant fields into a single string for embedding.

    Args:
        book_dict: Dictionary with book data

    Returns:
        Combined text string
    """
    parts = []

    # Add title (most important, add twice for weight)
    if book_dict.get('title'):
        parts.append(book_dict['title'])
        parts.append(book_dict['title'])

    # Add author
    if book_dict.get('author'):
        parts.append(book_dict['author'])

    # Add description (very important for semantic search)
    if book_dict.get('description'):
        parts.append(book_dict['description'])

    # Add theme and genre
    if book_dict.get('theme'):
        parts.append(book_dict['theme'])
    if book_dict.get('genre'):
        parts.append(book_dict['genre'])
    if book_dict.get('subgenre'):
        parts.append(book_dict['subgenre'])

    # Add notes
    if book_dict.get('notes'):
        parts.append(book_dict['notes'])

    return " ".join(parts)


def create_dvd_text(dvd_dict: dict) -> str:
    """
    Create searchable text representation of a DVD.

    Combines all relevant fields into a single string for embedding.

    Args:
        dvd_dict: Dictionary with DVD data

    Returns:
        Combined text string
    """
    parts = []

    # Add title (most important, add twice for weight)
    if dvd_dict.get('title'):
        parts.append(dvd_dict['title'])
        parts.append(dvd_dict['title'])

    # Add director
    if dvd_dict.get('director'):
        parts.append(dvd_dict['director'])

    # Add description (very important for semantic search)
    if dvd_dict.get('description'):
        parts.append(dvd_dict['description'])

    # Add theme and genre
    if dvd_dict.get('theme'):
        parts.append(dvd_dict['theme'])
    if dvd_dict.get('genre'):
        parts.append(dvd_dict['genre'])
    if dvd_dict.get('subgenre'):
        parts.append(dvd_dict['subgenre'])

    # Add notes
    if dvd_dict.get('notes'):
        parts.append(dvd_dict['notes'])

    return " ".join(parts)


def semantic_search(
    query: str,
    books: List[dict],
    top_k: int = 10
) -> List[Tuple[dict, float]]:
    """
    Perform semantic search on books.

    Finds books that are semantically similar to the query, not just keyword matches.

    Args:
        query: Search query (e.g., "books about friendship and loyalty")
        books: List of book dictionaries
        top_k: Number of top results to return

    Returns:
        List of (book_dict, similarity_score) tuples, sorted by relevance

    Example:
        >>> query = "stories about courage in difficult times"
        >>> results = semantic_search(query, all_books, top_k=5)
        >>> for book, score in results:
        ...     print(f"{book['title']}: {score:.2f}")
    """
    if not books or not query:
        return []

    # Get model
    model = get_embedding_model()

    # Create book texts
    book_texts = [create_book_text(book) for book in books]

    # Filter out empty texts
    valid_indices = [i for i, text in enumerate(book_texts) if text.strip()]
    if not valid_indices:
        return []

    valid_books = [books[i] for i in valid_indices]
    valid_texts = [book_texts[i] for i in valid_indices]

    # Encode query and books
    query_embedding = model.encode([query])
    book_embeddings = model.encode(valid_texts)

    # Calculate similarities
    similarities = cosine_similarity(query_embedding, book_embeddings)[0]

    # Sort by similarity (descending)
    sorted_indices = np.argsort(similarities)[::-1]

    # Return top_k results
    results = [
        (valid_books[idx], float(similarities[idx]))
        for idx in sorted_indices[:top_k]
        if similarities[idx] > 0.1  # Filter very low similarities
    ]

    return results


def semantic_search_dvd(
    query: str,
    dvds: List[dict],
    top_k: int = 10
) -> List[Tuple[dict, float]]:
    """
    Perform semantic search on DVDs.

    Finds DVDs that are semantically similar to the query, not just keyword matches.

    Args:
        query: Search query (e.g., "documentaries about climate change")
        dvds: List of DVD dictionaries
        top_k: Number of top results to return

    Returns:
        List of (dvd_dict, similarity_score) tuples, sorted by relevance

    Example:
        >>> query = "films about social justice"
        >>> results = semantic_search_dvd(query, all_dvds, top_k=5)
        >>> for dvd, score in results:
        ...     print(f"{dvd['title']}: {score:.2f}")
    """
    if not dvds or not query:
        return []

    # Get model
    model = get_embedding_model()

    # Create DVD texts
    dvd_texts = [create_dvd_text(dvd) for dvd in dvds]

    # Filter out empty texts
    valid_indices = [i for i, text in enumerate(dvd_texts) if text.strip()]
    if not valid_indices:
        return []

    valid_dvds = [dvds[i] for i in valid_indices]
    valid_texts = [dvd_texts[i] for i in valid_indices]

    # Encode query and DVDs
    query_embedding = model.encode([query])
    dvd_embeddings = model.encode(valid_texts)

    # Calculate similarities
    similarities = cosine_similarity(query_embedding, dvd_embeddings)[0]

    # Sort by similarity (descending)
    sorted_indices = np.argsort(similarities)[::-1]

    # Return top_k results
    results = [
        (valid_dvds[idx], float(similarities[idx]))
        for idx in sorted_indices[:top_k]
        if similarities[idx] > 0.1  # Filter very low similarities
    ]

    return results
