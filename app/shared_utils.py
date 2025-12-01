"""
Shared utilities for the Library application.

Contains common styling, helper functions, and configurations.
"""
import streamlit as st


def apply_custom_styling():
    """Apply custom CSS styling to the app."""
    st.markdown("""
    <style>
        /* Main container */
        .main > div {
            padding-top: 1rem;
        }

        /* Headers */
        h1 {
            color: #1f77b4;
            padding-bottom: 0.5rem;
            border-bottom: 3px solid #1f77b4;
            margin-bottom: 1.5rem;
        }

        h2 {
            color: #2c3e50;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }

        h3 {
            color: #34495e;
            margin-top: 1rem;
        }

        /* Tabs styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 1rem;
            background-color: #f8f9fa;
            padding: 0.5rem;
            border-radius: 0.5rem;
        }

        .stTabs [data-baseweb="tab"] {
            padding: 0.75rem 1.5rem;
            font-size: 1rem;
            font-weight: 500;
            border-radius: 0.3rem;
        }

        .stTabs [data-baseweb="tab"]:hover {
            background-color: #e9ecef;
        }

        /* Buttons */
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            font-weight: 500;
        }

        .stButton>button[kind="primary"] {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }

        /* Special boxes */
        .info-box {
            background: linear-gradient(135deg, #667eea15 0%, #764ba215 100%);
            padding: 1.5rem;
            border-radius: 0.75rem;
            border-left: 4px solid #667eea;
            margin-bottom: 1.5rem;
        }

        .isbn-box {
            background-color: #f0f9ff;
            padding: 1.25rem;
            border-radius: 0.75rem;
            border: 2px solid #bfdbfe;
            margin-bottom: 1.5rem;
        }

        /* Dataframe styling */
        .stDataFrame {
            border-radius: 0.5rem;
            overflow: hidden;
        }

        /* Form styling */
        .stForm {
            background-color: #f8f9fa;
            padding: 1.5rem;
            border-radius: 0.75rem;
            border: 1px solid #dee2e6;
        }

        /* Sidebar */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
        }

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] label {
            color: white !important;
        }

        /* Input fields */
        .stTextInput>div>div>input,
        .stTextArea>div>div>textarea {
            border-radius: 0.5rem;
        }

        /* Metrics */
        [data-testid="stMetricValue"] {
            font-size: 2rem;
            font-weight: 700;
        }
    </style>
    """, unsafe_allow_html=True)


def render_page_header(title: str, icon: str, description: str = None):
    """
    Render a consistent page header.

    Args:
        title: Page title
        icon: Emoji icon
        description: Optional description text
    """
    st.title(f"{icon} {title}")
    if description:
        st.markdown(f"*{description}*")
    st.markdown("---")


def get_column_mapping():
    """Get Danish column name mappings."""
    return {
        "id": "ID",
        "book_number": "Bognr.",
        "title": "Titel",
        "author": "Forfatter",
        "director": "Instruktør",
        "location": "Placering",
        "borrowed_count": "Udlånt",
        "total_count": "I alt",
        "theme": "Tema",
        "geographical_area": "Geografisk område",
        "publication_year": "År",
        "genre": "Genre",
        "subgenre": "Undergenre",
        "material_type": "Materialetype",
        "notes": "Noter",
        "description": "Beskrivelse"
    }


def to_none_if_empty(value):
    """Convert empty string or zero to None."""
    return value if value else None


def build_data_dict(**kwargs):
    """Build data dictionary, converting empty values to None."""
    return {k: to_none_if_empty(v) if k != "borrowed_count" and k != "total_count" else v
            for k, v in kwargs.items()}


def render_detail_field(label, value, fallback="N/A"):
    """Render a detail field with fallback."""
    st.markdown(f"**{label}:** {value if value else fallback}")
