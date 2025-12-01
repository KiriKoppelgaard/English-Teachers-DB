"""
Engelsklærernes Bibliotek - Administrer Materialer

Tilføj, rediger og slet bøger og DVD'er.
"""
import streamlit as st
import pandas as pd

from TeacherLibrary.data.database import SessionLocal
from TeacherLibrary.models.crud import book_crud, dvd_crud
from TeacherLibrary.models.validators import BookSchema, DVDSchema
from TeacherLibrary.data.fetch_isbn import fetch_book_by_isbn
from app.shared_utils import apply_custom_styling, render_page_header, get_column_mapping, build_data_dict

# Page config
st.set_page_config(
    page_title="Administrer Materialer - Engelsklærernes Bibliotek",
    page_icon="✏️",
    layout="wide"
)

# Apply styling
apply_custom_styling()

# Render header
render_page_header(
    "Administrer Materialer",
    "✏️",
    "Tilføj, rediger og slet bøger og DVD'er"
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
        # === BOOKS MANAGEMENT ===

        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["➕ Tilføj Ny Bog", "✏️ Rediger Bog", "🗑️ Slet Bog"])

        # ===== ADD BOOK TAB =====
        with tab1:
            st.subheader("Tilføj Ny Bog")

            # ISBN lookup box
            st.markdown("**📚 ISBN Opslag** - Hent automatisk bogoplysninger fra Google Books")

            col1, col2 = st.columns([3, 1])
            with col1:
                isbn_input = st.text_input(
                    "ISBN",
                    placeholder="978-0-123456-78-9",
                    help="Indtast ISBN-10 eller ISBN-13",
                    label_visibility="collapsed",
                    key="isbn_input_add"
                )
            with col2:
                lookup_isbn = st.button("🔍 Søg ISBN", use_container_width=True, key="lookup_isbn_add")

            # Initialize session state for form fields
            if "book_form_data" not in st.session_state:
                st.session_state.book_form_data = {}

            # Handle ISBN lookup
            if lookup_isbn and isbn_input:
                with st.spinner("Henter bogoplysninger..."):
                    book_data = fetch_book_by_isbn(isbn_input)
                    if book_data:
                        st.session_state.book_form_data = {
                            "title": book_data.get("title", ""),
                            "author": book_data.get("author", ""),
                            "publication_year": book_data.get("publication_year"),
                            "description": book_data.get("description", ""),
                            "genre": book_data.get("categories", "")
                        }
                        st.success("✅ Bogoplysninger hentet!")
                    else:
                        st.error("❌ Kunne ikke finde bog med dette ISBN")

            # Book form
            with st.form("add_book_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                with col1:
                    book_number = st.number_input("Bognr.", min_value=0, value=None, step=1, placeholder="Valgfrit")
                    title = st.text_input(
                        "Titel *",
                        value=st.session_state.book_form_data.get("title", ""),
                        placeholder="Bogens titel"
                    )
                    author = st.text_input(
                        "Forfatter",
                        value=st.session_state.book_form_data.get("author", ""),
                        placeholder="Forfatterens navn"
                    )
                    location = st.text_input("Placering", placeholder="F.eks. gml.kælder")
                    theme = st.text_input("Tema", placeholder="Bogens tema")
                    geographical_area = st.text_input("Geografisk område", placeholder="F.eks. USA, UK, Danmark")
                    publication_year = st.number_input(
                        "Udgivelsesår",
                        min_value=1000,
                        max_value=9999,
                        value=st.session_state.book_form_data.get("publication_year"),
                        step=1
                    )

                with col2:
                    borrowed_count = st.number_input("Udlånt (antal)", min_value=0, value=0, step=1)
                    total_count = st.number_input("I alt (antal)", min_value=0, value=0, step=1)
                    genre = st.text_input(
                        "Genre",
                        value=st.session_state.book_form_data.get("genre", ""),
                        placeholder="F.eks. Fiction, Non-fiction"
                    )
                    subgenre = st.text_input("Undergenre", placeholder="F.eks. Mystery, Biography")
                    material_type_field = st.text_input("Materialetype", placeholder="F.eks. Hardcover, Paperback")

                description = st.text_area(
                    "Beskrivelse",
                    value=st.session_state.book_form_data.get("description", ""),
                    placeholder="Beskrivelse af bogens indhold",
                    height=100
                )
                notes = st.text_area("Noter", placeholder="Eventuelle noter", height=100)

                submitted = st.form_submit_button("💾 Gem Bog", use_container_width=True)

                if submitted:
                    if not title:
                        st.error("❌ Titel er påkrævet!")
                    else:
                        try:
                            book_data = build_data_dict(
                                book_number=book_number, title=title, author=author, location=location,
                                borrowed_count=borrowed_count, total_count=total_count, theme=theme,
                                geographical_area=geographical_area, publication_year=publication_year,
                                genre=genre, subgenre=subgenre, material_type=material_type_field,
                                notes=notes, description=description
                            )
                            BookSchema(**book_data)
                            book_crud.create(db, book_data)
                            st.success(f"✅ Bogen '{title}' er tilføjet!")
                            st.session_state.book_form_data = {}
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fejl ved tilføjelse: {str(e)}")

        # ===== EDIT BOOK TAB =====
        with tab2:
            st.subheader("Rediger Bog")

            # Get all books
            all_books = book_crud.get_all(db)

            if not all_books:
                st.info("📚 Ingen bøger i samlingen endnu.")
            else:
                # Create book selection dropdown
                book_options = {f"{book.title} - {book.author}": book.id for book in all_books}
                selected_book_name = st.selectbox(
                    "Vælg bog at redigere:",
                    options=list(book_options.keys()),
                    key="edit_book_select"
                )

                if selected_book_name:
                    book_id = book_options[selected_book_name]
                    book = book_crud.get(db, book_id)

                    if book:
                        st.markdown("---")

                        # Edit form
                        with st.form("edit_book_form"):
                            col1, col2 = st.columns(2)

                            with col1:
                                book_number = st.number_input("Bognr.", min_value=0, value=book.book_number if book.book_number else None, step=1)
                                title = st.text_input("Titel *", value=book.title or "")
                                author = st.text_input("Forfatter", value=book.author or "")
                                location = st.text_input("Placering", value=book.location or "")
                                theme = st.text_input("Tema", value=book.theme or "")
                                geographical_area = st.text_input("Geografisk område", value=book.geographical_area or "")
                                publication_year = st.number_input(
                                    "Udgivelsesår",
                                    min_value=1000,
                                    max_value=9999,
                                    value=book.publication_year if book.publication_year else None,
                                    step=1
                                )

                            with col2:
                                borrowed_count = st.number_input("Udlånt (antal)", min_value=0, value=book.borrowed_count, step=1)
                                total_count = st.number_input("I alt (antal)", min_value=0, value=book.total_count, step=1)
                                genre = st.text_input("Genre", value=book.genre or "")
                                subgenre = st.text_input("Undergenre", value=book.subgenre or "")
                                material_type_field = st.text_input("Materialetype", value=book.material_type or "")

                            description = st.text_area("Beskrivelse", value=book.description or "", height=100)
                            notes = st.text_area("Noter", value=book.notes or "", height=100)

                            update_submitted = st.form_submit_button("💾 Gem Ændringer", use_container_width=True)

                            if update_submitted:
                                if not title:
                                    st.error("❌ Titel er påkrævet!")
                                else:
                                    try:
                                        update_data = build_data_dict(
                                            book_number=book_number, title=title, author=author, location=location,
                                            borrowed_count=borrowed_count, total_count=total_count, theme=theme,
                                            geographical_area=geographical_area, publication_year=publication_year,
                                            genre=genre, subgenre=subgenre, material_type=material_type_field,
                                            notes=notes, description=description
                                        )
                                        BookSchema(**update_data)
                                        book_crud.update(db, book_id, update_data)
                                        st.success(f"✅ Bogen '{title}' er opdateret!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Fejl ved opdatering: {str(e)}")

        # ===== DELETE BOOK TAB =====
        with tab3:
            st.subheader("Slet Bog")

            # Get all books
            all_books = book_crud.get_all(db)

            if not all_books:
                st.info("📚 Ingen bøger i samlingen endnu.")
            else:
                st.warning("⚠️ Advarsel: Denne handling kan ikke fortrydes!")

                # Create book selection dropdown
                book_options = {f"{book.title} - {book.author}": book.id for book in all_books}
                selected_book_name = st.selectbox(
                    "Vælg bog at slette:",
                    options=list(book_options.keys()),
                    key="delete_book_select"
                )

                if selected_book_name:
                    book_id = book_options[selected_book_name]
                    book = book_crud.get(db, book_id)

                    if book:
                        # Show book details
                        st.markdown("---")
                        st.markdown("**Bog detaljer:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Titel:** {book.title}")
                            st.write(f"**Forfatter:** {book.author}")
                            st.write(f"**Genre:** {book.genre or 'N/A'}")
                        with col2:
                            st.write(f"**År:** {book.publication_year or 'N/A'}")
                            st.write(f"**Tema:** {book.theme or 'N/A'}")
                            st.write(f"**Område:** {book.geographical_area or 'N/A'}")

                        st.markdown("---")

                        # Confirmation
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if st.button("🗑️ Slet Bog", use_container_width=True, type="primary"):
                                try:
                                    book_crud.delete(db, book_id)
                                    st.success(f"✅ Bogen '{book.title}' er slettet!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fejl ved sletning: {str(e)}")

    else:
        # === DVD MANAGEMENT ===

        # Tabs for different actions
        tab1, tab2, tab3 = st.tabs(["➕ Tilføj Ny DVD", "✏️ Rediger DVD", "🗑️ Slet DVD"])

        # ===== ADD DVD TAB =====
        with tab1:
            st.subheader("Tilføj Ny DVD")

            with st.form("add_dvd_form", clear_on_submit=True):
                col1, col2 = st.columns(2)

                with col1:
                    title = st.text_input("Titel *", placeholder="DVD-titel")
                    director = st.text_input("Instruktør *", placeholder="Instruktørens navn")
                    theme = st.text_input("Tema", placeholder="DVD'ens tema")
                    geographical_area = st.text_input("Geografisk område", placeholder="F.eks. USA, UK, Danmark")
                    publication_year = st.number_input(
                        "Udgivelsesår",
                        min_value=1000,
                        max_value=9999,
                        value=None,
                        step=1
                    )

                with col2:
                    genre = st.text_input("Genre", placeholder="F.eks. Documentary, Drama")
                    subgenre = st.text_input("Undergenre", placeholder="F.eks. Historical, Educational")
                    material_type_field = st.text_input("Materialetype", placeholder="F.eks. DVD, Blu-ray, Reference Disc")

                description = st.text_area("Beskrivelse", placeholder="Beskrivelse af DVD'ens indhold", height=100)
                notes = st.text_area("Noter", placeholder="Eventuelle noter", height=100)

                submitted = st.form_submit_button("💾 Gem DVD", use_container_width=True)

                if submitted:
                    if not title or not director:
                        st.error("❌ Titel og instruktør er påkrævet!")
                    else:
                        try:
                            dvd_data = build_data_dict(
                                title=title, director=director, theme=theme, geographical_area=geographical_area,
                                publication_year=publication_year, genre=genre, subgenre=subgenre,
                                material_type=material_type_field, notes=notes, description=description
                            )
                            DVDSchema(**dvd_data)
                            dvd_crud.create(db, dvd_data)
                            st.success(f"✅ DVD'en '{title}' er tilføjet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fejl ved tilføjelse: {str(e)}")

        # ===== EDIT DVD TAB =====
        with tab2:
            st.subheader("Rediger DVD")

            # Get all DVDs
            all_dvds = dvd_crud.get_all(db)

            if not all_dvds:
                st.info("📀 Ingen DVD'er i samlingen endnu.")
            else:
                # Create DVD selection dropdown
                dvd_options = {f"{dvd.title} - {dvd.director}": dvd.id for dvd in all_dvds}
                selected_dvd_name = st.selectbox(
                    "Vælg DVD at redigere:",
                    options=list(dvd_options.keys()),
                    key="edit_dvd_select"
                )

                if selected_dvd_name:
                    dvd_id = dvd_options[selected_dvd_name]
                    dvd = dvd_crud.get(db, dvd_id)

                    if dvd:
                        st.markdown("---")

                        # Edit form
                        with st.form("edit_dvd_form"):
                            col1, col2 = st.columns(2)

                            with col1:
                                title = st.text_input("Titel *", value=dvd.title or "")
                                director = st.text_input("Instruktør *", value=dvd.director or "")
                                theme = st.text_input("Tema", value=dvd.theme or "")
                                geographical_area = st.text_input("Geografisk område", value=dvd.geographical_area or "")
                                publication_year = st.number_input(
                                    "Udgivelsesår",
                                    min_value=1000,
                                    max_value=9999,
                                    value=dvd.publication_year if dvd.publication_year else None,
                                    step=1
                                )

                            with col2:
                                genre = st.text_input("Genre", value=dvd.genre or "")
                                subgenre = st.text_input("Undergenre", value=dvd.subgenre or "")
                                material_type_field = st.text_input("Materialetype", value=dvd.material_type or "")

                            description = st.text_area("Beskrivelse", value=dvd.description or "", height=100)
                            notes = st.text_area("Noter", value=dvd.notes or "", height=100)

                            update_submitted = st.form_submit_button("💾 Gem Ændringer", use_container_width=True)

                            if update_submitted:
                                if not title or not director:
                                    st.error("❌ Titel og instruktør er påkrævet!")
                                else:
                                    try:
                                        update_data = build_data_dict(
                                            title=title, director=director, theme=theme, geographical_area=geographical_area,
                                            publication_year=publication_year, genre=genre, subgenre=subgenre,
                                            material_type=material_type_field, notes=notes, description=description
                                        )
                                        DVDSchema(**update_data)
                                        dvd_crud.update(db, dvd_id, update_data)
                                        st.success(f"✅ DVD'en '{title}' er opdateret!")
                                        st.rerun()
                                    except Exception as e:
                                        st.error(f"❌ Fejl ved opdatering: {str(e)}")

        # ===== DELETE DVD TAB =====
        with tab3:
            st.subheader("Slet DVD")

            # Get all DVDs
            all_dvds = dvd_crud.get_all(db)

            if not all_dvds:
                st.info("📀 Ingen DVD'er i samlingen endnu.")
            else:
                st.warning("⚠️ Advarsel: Denne handling kan ikke fortrydes!")

                # Create DVD selection dropdown
                dvd_options = {f"{dvd.title} - {dvd.director}": dvd.id for dvd in all_dvds}
                selected_dvd_name = st.selectbox(
                    "Vælg DVD at slette:",
                    options=list(dvd_options.keys()),
                    key="delete_dvd_select"
                )

                if selected_dvd_name:
                    dvd_id = dvd_options[selected_dvd_name]
                    dvd = dvd_crud.get(db, dvd_id)

                    if dvd:
                        # Show DVD details
                        st.markdown("---")
                        st.markdown("**DVD detaljer:**")
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**Titel:** {dvd.title}")
                            st.write(f"**Instruktør:** {dvd.director}")
                            st.write(f"**Genre:** {dvd.genre or 'N/A'}")
                        with col2:
                            st.write(f"**År:** {dvd.publication_year or 'N/A'}")
                            st.write(f"**Tema:** {dvd.theme or 'N/A'}")
                            st.write(f"**Område:** {dvd.geographical_area or 'N/A'}")

                        st.markdown("---")

                        # Confirmation
                        col1, col2 = st.columns([1, 3])
                        with col1:
                            if st.button("🗑️ Slet DVD", use_container_width=True, type="primary"):
                                try:
                                    dvd_crud.delete(db, dvd_id)
                                    st.success(f"✅ DVD'en '{dvd.title}' er slettet!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fejl ved sletning: {str(e)}")

finally:
    db.close()
