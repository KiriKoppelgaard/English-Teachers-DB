"""
Engelsklærernes Bibliotek - Søg Materialer

Søg, vis, rediger og slet bøger og DVD'er.
"""
import streamlit as st
import pandas as pd

from TeacherLibrary.data.database import SessionLocal
from TeacherLibrary.models.crud import book_crud, dvd_crud
from TeacherLibrary.data.semantic_search import semantic_search, semantic_search_dvd
from app.shared_utils import apply_custom_styling, render_page_header, get_column_mapping

# Page config
st.set_page_config(
    page_title="Søg Materialer - Engelsklærernes Bibliotek",
    page_icon="🔍",
    layout="wide"
)

# Apply styling
apply_custom_styling()

# Render header
render_page_header(
    "Søg Materialer",
    "🔍",
    "Søg i din samling"
)

# Material type selector
material_type = st.radio(
    "Vælg materialetype:",
    ["📖 Bøger", "📀 DVD'er"],
    horizontal=True,
    label_visibility="collapsed"
)

is_books = material_type == "📖 Bøger"

# Get database session
db = SessionLocal()

try:
    if is_books:
        # === BOOKS SECTION ===
        st.subheader("Søg i Bogsamlingen")

        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "Søgetekst",
                placeholder="Søg efter titel, forfatter, tema, etc.",
                help="Indtast søgeord for at filtrere bøger",
                key="book_search"
            )

        with col2:
            use_semantic = st.checkbox(
                "Smart søgning",
                value=False,
                help="Find bøger baseret på betydning og indhold, ikke kun nøgleord",
                key="book_semantic"
            )

        # Sorting and filtering
        col1, col2 = st.columns(2)

        with col1:
            sort_options = {
                "title": "Titel",
                "author": "Forfatter",
                "theme": "Tema",
                "geographical_area": "Geografisk område",
                "publication_year": "Udgivelsesår",
                "genre": "Genre"
            }
            sort_by = st.selectbox("Sortér efter", options=list(sort_options.keys()),
                                  format_func=lambda x: sort_options[x], key="book_sort")

        with col2:
            all_items = book_crud.get_all(db)
            genres = sorted(set(item.genre for item in all_items if item.genre))
            selected_genre = st.selectbox("Filtrér efter genre", ["Alle"] + genres, key="book_genre")

        # Get and display items
        if use_semantic and search_query:
            all_items_dict = [item.to_dict() for item in all_items]
            results = semantic_search(search_query, all_items_dict, top_k=50)
            items = [item[0] for item in results]
            if selected_genre != "Alle":
                items = [item for item in items if item.get("genre") == selected_genre]
        else:
            filters = {}
            if selected_genre != "Alle":
                filters["genre"] = selected_genre
            items = book_crud.get_all(db, search=search_query if search_query else None, sort_by=sort_by, **filters)
            items = [item.to_dict() for item in items]

        st.info(f"📊 Fundet {len(items)} bøger")

        if items:
            df = pd.DataFrame(items)
            column_order = ["book_number", "title", "author", "location", "borrowed_count", "total_count", "theme", "geographical_area", "publication_year", "genre", "subgenre", "material_type"]
            display_columns = [col for col in column_order if col in df.columns]
            df_display = df[display_columns]
            column_mapping = get_column_mapping()
            df_display = df_display.rename(columns=column_mapping)
            st.dataframe(df_display, use_container_width=True)

            # Detail view section
            st.markdown("---")
            st.subheader("📖 Detaljevisning")

            # Create selection dropdown
            book_options = {f"{item['title']} - {item.get('author', 'Ukendt')} ({item.get('book_number', item['id'])})"
                          : item['id'] for item in items}
            selected_book = st.selectbox(
                "Vælg bog for at se detaljer:",
                options=list(book_options.keys()),
                key="book_detail_select"
            )

            if selected_book:
                book_id = book_options[selected_book]
                book = book_crud.get(db, book_id)

                if book:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📚 Grundlæggende Information")
                        st.markdown(f"**Bognr.:** {book.book_number if book.book_number else 'N/A'}")
                        st.markdown(f"**Titel:** {book.title}")
                        st.markdown(f"**Forfatter:** {book.author if book.author else 'Ukendt'}")
                        st.markdown(f"**Placering:** {book.location if book.location else 'N/A'}")
                        st.markdown(f"**År:** {book.publication_year if book.publication_year else 'N/A'}")

                        st.markdown("### 📊 Beholdning")
                        st.markdown(f"**Udlånt:** {book.borrowed_count}")
                        st.markdown(f"**I alt:** {book.total_count}")
                        if book.total_count > 0:
                            available = book.total_count - book.borrowed_count
                            st.markdown(f"**Tilgængelige:** {available}")

                    with col2:
                        st.markdown("### 🏷️ Kategorisering")
                        st.markdown(f"**Genre:** {book.genre if book.genre else 'N/A'}")
                        st.markdown(f"**Undergenre:** {book.subgenre if book.subgenre else 'N/A'}")
                        st.markdown(f"**Tema:** {book.theme if book.theme else 'N/A'}")
                        st.markdown(f"**Geografisk område:** {book.geographical_area if book.geographical_area else 'N/A'}")
                        st.markdown(f"**Materialetype:** {book.material_type if book.material_type else 'N/A'}")

                    if book.description:
                        st.markdown("### 📝 Beskrivelse")
                        st.write(book.description)

                    if book.notes:
                        st.markdown("### 📌 Noter")
                        st.write(book.notes)
        else:
            st.info("Ingen bøger fundet. Prøv en anden søgning.")

    else:
        # === DVDs SECTION ===
        st.subheader("Søg i DVD-samlingen")

        col1, col2 = st.columns([3, 1])

        with col1:
            search_query = st.text_input(
                "Søgetekst",
                placeholder="Søg efter titel, instruktør, tema, etc.",
                help="Indtast søgeord for at filtrere DVD'er",
                key="dvd_search"
            )

        with col2:
            use_semantic = st.checkbox(
                "Smart søgning",
                value=False,
                help="Find DVD'er baseret på betydning og indhold, ikke kun nøgleord",
                key="dvd_semantic"
            )

        col1, col2 = st.columns(2)

        with col1:
            sort_options = {
                "title": "Titel", "director": "Instruktør", "theme": "Tema",
                "geographical_area": "Geografisk område", "publication_year": "Udgivelsesår", "genre": "Genre"
            }
            sort_by = st.selectbox("Sortér efter", options=list(sort_options.keys()),
                                  format_func=lambda x: sort_options[x], key="dvd_sort")

        with col2:
            all_items = dvd_crud.get_all(db)
            genres = sorted(set(item.genre for item in all_items if item.genre))
            selected_genre = st.selectbox("Filtrér efter genre", ["Alle"] + genres, key="dvd_genre")

        if use_semantic and search_query:
            all_items_dict = [item.to_dict() for item in all_items]
            results = semantic_search_dvd(search_query, all_items_dict, top_k=50)
            items = [item[0] for item in results]
            if selected_genre != "Alle":
                items = [item for item in items if item.get("genre") == selected_genre]
        else:
            filters = {}
            if selected_genre != "Alle":
                filters["genre"] = selected_genre
            items = dvd_crud.get_all(db, search=search_query if search_query else None, sort_by=sort_by, **filters)
            items = [item.to_dict() for item in items]

        st.info(f"📊 Fundet {len(items)} DVD'er")

        if items:
            df = pd.DataFrame(items)
            column_order = ["title", "director", "theme", "geographical_area", "publication_year", "genre", "subgenre", "material_type"]
            display_columns = [col for col in column_order if col in df.columns]
            df_display = df[display_columns]
            column_mapping = get_column_mapping()
            df_display = df_display.rename(columns=column_mapping)
            st.dataframe(df_display, use_container_width=True)

            # Detail view section
            st.markdown("---")
            st.subheader("📀 Detaljevisning")

            # Create selection dropdown
            dvd_options = {f"{item['title']} - {item.get('director', 'Ukendt')} ({item['id']})"
                          : item['id'] for item in items}
            selected_dvd = st.selectbox(
                "Vælg DVD for at se detaljer:",
                options=list(dvd_options.keys()),
                key="dvd_detail_select"
            )

            if selected_dvd:
                dvd_id = dvd_options[selected_dvd]
                dvd = dvd_crud.get(db, dvd_id)

                if dvd:
                    col1, col2 = st.columns(2)

                    with col1:
                        st.markdown("### 📀 Grundlæggende Information")
                        st.markdown(f"**Titel:** {dvd.title}")
                        st.markdown(f"**Instruktør:** {dvd.director if dvd.director else 'Ukendt'}")
                        st.markdown(f"**År:** {dvd.publication_year if dvd.publication_year else 'N/A'}")

                    with col2:
                        st.markdown("### 🏷️ Kategorisering")
                        st.markdown(f"**Genre:** {dvd.genre if dvd.genre else 'N/A'}")
                        st.markdown(f"**Undergenre:** {dvd.subgenre if dvd.subgenre else 'N/A'}")
                        st.markdown(f"**Tema:** {dvd.theme if dvd.theme else 'N/A'}")
                        st.markdown(f"**Geografisk område:** {dvd.geographical_area if dvd.geographical_area else 'N/A'}")
                        st.markdown(f"**Materialetype:** {dvd.material_type if dvd.material_type else 'N/A'}")

                    if dvd.description:
                        st.markdown("### 📝 Beskrivelse")
                        st.write(dvd.description)

                    if dvd.notes:
                        st.markdown("### 📌 Noter")
                        st.write(dvd.notes)
        else:
            st.info("Ingen DVD'er fundet. Prøv en anden søgning.")

finally:
    db.close()
