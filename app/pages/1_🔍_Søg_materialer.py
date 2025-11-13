"""
Engelsklærernes Bibliotek - Søg Materialer

Søg, vis, rediger og slet bøger og DVD'er.
"""
import streamlit as st
import pandas as pd

from TeacherLibrary.data.database import SessionLocal
from TeacherLibrary.models.crud import book_crud, dvd_crud
from TeacherLibrary.models.validators import BookSchema, DVDSchema
from TeacherLibrary.data.semantic_search import semantic_search, semantic_search_dvd
from TeacherLibrary.data.make_dataset import export_to_csv, export_to_excel, import_from_file
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
    "Søg, rediger og administrer din samling"
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
        col1, col2, col3 = st.columns(3)

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

        with col3:
            st.write("")
            st.write("")
            col_a, col_b = st.columns(2)
            with col_a:
                items_data = [item.to_dict() for item in all_items]
                if items_data:
                    csv_data = export_to_csv(items_data)
                    st.download_button(
                        label="📥 CSV",
                        data=csv_data,
                        file_name="boger.csv",
                        mime="text/csv",
                        use_container_width=True,
                        key="book_csv"
                    )
            with col_b:
                if items_data:
                    excel_data = export_to_excel(items_data, "Bøger")
                    st.download_button(
                        label="📥 Excel",
                        data=excel_data,
                        file_name="boger.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                        key="book_excel"
                    )

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
            column_order = ["title", "author", "theme", "geographical_area", "publication_year", "genre", "subgenre", "material_type"]
            display_columns = [col for col in column_order if col in df.columns]
            df_display = df[display_columns]
            column_mapping = get_column_mapping()
            df_display = df_display.rename(columns=column_mapping)
            st.dataframe(df_display, use_container_width=True)

            st.markdown("---")
            st.subheader("⚙️ Handlinger")

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                st.markdown("### 📖 Vis / Rediger")
                item_titles = [f"{item['title']} - {item['author']} (ID: {item['id']})" for item in items]
                selected_item = st.selectbox("Vælg bog", item_titles, key="book_edit_select")

                if selected_item:
                    item_id = int(selected_item.split("ID: ")[1].rstrip(")"))
                    item = book_crud.get(db, item_id)

                    with st.form(f"edit_book_{item_id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            title = st.text_input("Titel *", value=item.title)
                            author = st.text_input("Forfatter *", value=item.author)
                            theme = st.text_input("Tema", value=item.theme or "")
                            geographical_area = st.text_input("Geografisk område", value=item.geographical_area or "")
                            publication_year = st.number_input("Udgivelsesår", min_value=1000, max_value=9999,
                                                              value=item.publication_year if item.publication_year else None, step=1)
                        with col2:
                            genre = st.text_input("Genre", value=item.genre or "")
                            subgenre = st.text_input("Undergenre", value=item.subgenre or "")
                            material_type = st.text_input("Materialetype", value=item.material_type or "")
                        description = st.text_area("Beskrivelse", value=item.description or "", height=100)
                        notes = st.text_area("Noter", value=item.notes or "", height=100)

                        if st.form_submit_button("💾 Gem Ændringer", use_container_width=True):
                            if not title or not author:
                                st.error("❌ Titel og forfatter er påkrævet!")
                            else:
                                try:
                                    item_data = {
                                        "title": title, "author": author, "theme": theme if theme else None,
                                        "geographical_area": geographical_area if geographical_area else None,
                                        "publication_year": publication_year if publication_year else None,
                                        "genre": genre if genre else None, "subgenre": subgenre if subgenre else None,
                                        "material_type": material_type if material_type else None,
                                        "notes": notes if notes else None, "description": description if description else None
                                    }
                                    BookSchema(**item_data)
                                    book_crud.update(db, item_id, item_data)
                                    st.success(f"✅ Bogen '{title}' er opdateret!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fejl ved opdatering: {str(e)}")

            with action_col2:
                st.markdown("### 🗑️ Slet")
                st.warning("⚠️ Advarsel: Sletning kan ikke fortrydes!")
                selected_delete = st.selectbox("Vælg bog at slette", item_titles, key="book_delete_select")

                if selected_delete:
                    delete_id = int(selected_delete.split("ID: ")[1].rstrip(")"))
                    delete_item = book_crud.get(db, delete_id)
                    st.markdown(f"**Titel:** {delete_item.title}")
                    st.markdown(f"**Forfatter:** {delete_item.author}")

                    if st.button("🗑️ Slet Bog", type="primary", use_container_width=True, key="book_delete_btn"):
                        try:
                            book_crud.delete(db, delete_id)
                            st.success(f"✅ Bogen '{delete_item.title}' er slettet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fejl ved sletning: {str(e)}")

            st.markdown("---")
            st.markdown("### 📥 Importér Bøger")
            uploaded_file = st.file_uploader("Vælg CSV eller Excel fil", type=["csv", "xlsx"], key="book_import")
            if uploaded_file:
                file_type = "xlsx" if uploaded_file.name.endswith(".xlsx") else "csv"
                if st.button("📥 Importér Data", use_container_width=True, key="book_import_btn"):
                    try:
                        success_count, errors = import_from_file(uploaded_file, book_crud, db, file_type)
                        if errors:
                            st.warning(f"⚠️ Importeret {success_count} bøger med {len(errors)} fejl:")
                            for error in errors[:5]:
                                st.error(error)
                        else:
                            st.success(f"✅ Importeret {success_count} bøger!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Fejl ved import: {str(e)}")
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

        col1, col2, col3 = st.columns(3)

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

        with col3:
            st.write("")
            st.write("")
            col_a, col_b = st.columns(2)
            with col_a:
                items_data = [item.to_dict() for item in all_items]
                if items_data:
                    csv_data = export_to_csv(items_data)
                    st.download_button(
                        label="📥 CSV", data=csv_data, file_name="dvder.csv",
                        mime="text/csv", use_container_width=True, key="dvd_csv"
                    )
            with col_b:
                if items_data:
                    excel_data = export_to_excel(items_data, "DVD'er")
                    st.download_button(
                        label="📥 Excel", data=excel_data, file_name="dvder.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True, key="dvd_excel"
                    )

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

            st.markdown("---")
            st.subheader("⚙️ Handlinger")

            action_col1, action_col2 = st.columns(2)

            with action_col1:
                st.markdown("### 📀 Vis / Rediger")
                item_titles = [f"{item['title']} - {item['director']} (ID: {item['id']})" for item in items]
                selected_item = st.selectbox("Vælg DVD", item_titles, key="dvd_edit_select")

                if selected_item:
                    item_id = int(selected_item.split("ID: ")[1].rstrip(")"))
                    item = dvd_crud.get(db, item_id)

                    with st.form(f"edit_dvd_{item_id}"):
                        col1, col2 = st.columns(2)
                        with col1:
                            title = st.text_input("Titel *", value=item.title)
                            director = st.text_input("Instruktør *", value=item.director)
                            theme = st.text_input("Tema", value=item.theme or "")
                            geographical_area = st.text_input("Geografisk område", value=item.geographical_area or "")
                            publication_year = st.number_input("Udgivelsesår", min_value=1000, max_value=9999,
                                                              value=item.publication_year if item.publication_year else None, step=1)
                        with col2:
                            genre = st.text_input("Genre", value=item.genre or "")
                            subgenre = st.text_input("Undergenre", value=item.subgenre or "")
                            material_type = st.text_input("Materialetype", value=item.material_type or "")
                        description = st.text_area("Beskrivelse", value=item.description or "", height=100)
                        notes = st.text_area("Noter", value=item.notes or "", height=100)

                        if st.form_submit_button("💾 Gem Ændringer", use_container_width=True):
                            if not title or not director:
                                st.error("❌ Titel og instruktør er påkrævet!")
                            else:
                                try:
                                    item_data = {
                                        "title": title, "director": director, "theme": theme if theme else None,
                                        "geographical_area": geographical_area if geographical_area else None,
                                        "publication_year": publication_year if publication_year else None,
                                        "genre": genre if genre else None, "subgenre": subgenre if subgenre else None,
                                        "material_type": material_type if material_type else None,
                                        "notes": notes if notes else None, "description": description if description else None
                                    }
                                    DVDSchema(**item_data)
                                    dvd_crud.update(db, item_id, item_data)
                                    st.success(f"✅ DVD'en '{title}' er opdateret!")
                                    st.rerun()
                                except Exception as e:
                                    st.error(f"❌ Fejl ved opdatering: {str(e)}")

            with action_col2:
                st.markdown("### 🗑️ Slet")
                st.warning("⚠️ Advarsel: Sletning kan ikke fortrydes!")
                selected_delete = st.selectbox("Vælg DVD at slette", item_titles, key="dvd_delete_select")

                if selected_delete:
                    delete_id = int(selected_delete.split("ID: ")[1].rstrip(")"))
                    delete_item = dvd_crud.get(db, delete_id)
                    st.markdown(f"**Titel:** {delete_item.title}")
                    st.markdown(f"**Instruktør:** {delete_item.director}")

                    if st.button("🗑️ Slet DVD", type="primary", use_container_width=True, key="dvd_delete_btn"):
                        try:
                            dvd_crud.delete(db, delete_id)
                            st.success(f"✅ DVD'en '{delete_item.title}' er slettet!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Fejl ved sletning: {str(e)}")

            st.markdown("---")
            st.markdown("### 📥 Importér DVD'er")
            uploaded_file = st.file_uploader("Vælg CSV eller Excel fil", type=["csv", "xlsx"], key="dvd_import")
            if uploaded_file:
                file_type = "xlsx" if uploaded_file.name.endswith(".xlsx") else "csv"
                if st.button("📥 Importér Data", use_container_width=True, key="dvd_import_btn"):
                    try:
                        success_count, errors = import_from_file(uploaded_file, dvd_crud, db, file_type)
                        if errors:
                            st.warning(f"⚠️ Importeret {success_count} DVD'er med {len(errors)} fejl:")
                            for error in errors[:5]:
                                st.error(error)
                        else:
                            st.success(f"✅ Importeret {success_count} DVD'er!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Fejl ved import: {str(e)}")
        else:
            st.info("Ingen DVD'er fundet. Prøv en anden søgning.")

finally:
    db.close()
