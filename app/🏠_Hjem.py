"""
Engelsklærernes Bibliotek - Hjem

Hovedside for bibliotekssystemet.
"""
import streamlit as st

from TeacherLibrary.data.database import SessionLocal, init_db
from TeacherLibrary.models.crud import book_crud, dvd_crud
from app.shared_utils import apply_custom_styling, render_page_header

# Initialize database
init_db()

# Page config
st.set_page_config(
    page_title="Engelsklærernes Bibliotek",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styling
apply_custom_styling()

# Render header
render_page_header(
    "Engelsklærernes Bibliotek",
    "📚"
)

# Get statistics
db = SessionLocal()
try:
    total_books = len(book_crud.get_all(db))
    total_dvds = len(dvd_crud.get_all(db))
finally:
    db.close()

# Display statistics immediately after header
st.subheader("📊 Oversigt")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        label="📖 Bøger",
        value=total_books,
        help="Antal bøger i samlingen"
    )

with col2:
    st.metric(
        label="📀 DVD'er",
        value=total_dvds,
        help="Antal DVD'er i samlingen"
    )

with col3:
    st.metric(
        label="📚 Total",
        value=total_books + total_dvds,
        help="Samlet antal materialer"
    )

st.markdown("---")


# Welcome message
st.markdown("""
<div class="info-box">
    <h2 style="margin-top: 0;">👋 Velkommen!</h2>
    <p style="font-size: 1.1rem; margin-bottom: 0;">
        Dette er dit bibliotekssystem til håndtering af bøger og DVD'er.<br>
        Vælg en sektion fra menuen til venstre for at komme i gang.
    </p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

# Quick guide
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### 🔍 Søg Materialer

    **Find materialer hurtigt og nemt:**
    - ✨ **Smart søgning** - Find materialer baseret på indhold og betydning
    - 🔍 **Fritekstsøgning** - Søg efter titel, forfatter, instruktør, etc.
    - 📊 **Sortér og filtrér** - Organisér efter genre, år, tema
    - 📥 **Import/Export** - CSV og Excel support
    - 📋 **Se detaljer** - Vis alle oplysninger om hvert materiale

    Vælg mellem bøger og DVD'er i toppen af siden.
    """)

with col2:
    st.markdown("""
    ### ✏️ Administrer Materialer

    **Tilføj, rediger og slet materialer:**
    - ➕ **Tilføj** - Opret nye bøger og DVD'er
    - ✏️ **Rediger** - Opdater eksisterende materialer
    - 🗑️ **Slet** - Fjern materialer fra samlingen
    - 📚 **ISBN opslag** - Automatisk udfyldning for bøger
    - 📝 **Beskrivelser** - Tilføj detaljerede beskrivelser

    Vælg mellem bøger og DVD'er, derefter handling i tabs.
    """)

st.markdown("---")

# Help section
with st.expander("❓ Hjælp"):
    st.markdown("""
    ### Sådan Bruger Du Systemet

    **Søg Efter Materialer:**
    1. Klik på "🔍 Søg materialer" i menuen til venstre
    2. Vælg materialetype: 📖 Bøger eller 📀 DVD'er
    3. **Normal søgning**: Indtast nøgleord (titel, forfatter, instruktør, etc.)
    4. **Smart søgning**: Aktiver checkboxen for at søge efter betydning og indhold
       - Eksempel: "bøger om mod og retfærdighed"
       - Eksempel: "dokumentarer om klimaændringer"
    5. **Import/Export**: Brug CSV eller Excel knapperne til at eksportere eller importere data

    **Administrer Materialer:**
    1. Klik på "✏️ Administrer materialer" i menuen til venstre
    2. Vælg materialetype: 📖 Bøger eller 📀 DVD'er
    3. Vælg handling i tabs:
       - **➕ Tilføj**: Opret nye materialer
         - For bøger: brug ISBN opslag for automatisk udfyldning
         - Udfyld felterne (markeret med * er påkrævet)
         - Klik "Gem"
       - **✏️ Rediger**: Opdater eksisterende materialer
         - Vælg materiale fra dropdown
         - Rediger felterne
         - Klik "Gem Ændringer"
       - **🗑️ Slet**: Fjern materialer fra samlingen
         - Vælg materiale fra dropdown
         - Bekræft sletning
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: #6c757d;'>"
    "Engelsklærernes Bibliotek | Udviklet med Streamlit & Python"
    "</p>",
    unsafe_allow_html=True
)
