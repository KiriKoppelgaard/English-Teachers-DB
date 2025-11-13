"""
Dataset creation utilities for import/export operations.

This module handles data import from CSV/Excel and export to various formats,
following cookiecutter-data-science conventions for data processing.
"""
from io import BytesIO
from typing import List

import pandas as pd
from sqlalchemy.orm import Session

from TeacherLibrary.models.crud import CRUDBase


def export_to_excel(data: List[dict], sheet_name: str) -> BytesIO:
    """
    Export data to Excel file format.

    Args:
        data: List of dictionaries containing record data
        sheet_name: Name for the Excel sheet

    Returns:
        BytesIO object containing Excel file
    """
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    output.seek(0)
    return output


def export_to_csv(data: List[dict]) -> str:
    """
    Export data to CSV format.

    Args:
        data: List of dictionaries containing record data

    Returns:
        CSV string
    """
    df = pd.DataFrame(data)
    return df.to_csv(index=False)


def import_from_file(
    file, crud: CRUDBase, db: Session, file_type: str = "csv"
) -> tuple[int, List[str]]:
    """
    Import data from CSV or Excel file into database.

    This function processes external data files and loads them into the database,
    following the cookiecutter-data-science pattern for data ingestion.

    Args:
        file: File object to import
        crud: CRUD operations instance for the target model
        db: Database session
        file_type: Type of file ('csv' or 'excel')

    Returns:
        Tuple of (success_count, error_messages)
    """
    try:
        # Load data from file
        if file_type == "csv":
            df = pd.read_csv(file)
        else:  # excel
            df = pd.read_excel(file)

        # Clean data: replace NaN with None
        df = df.where(pd.notna(df), None)

        success_count = 0
        errors = []

        # Process each row
        for idx, row in df.iterrows():
            try:
                data = row.to_dict()
                # Remove id if present (auto-generated for new records)
                data.pop("id", None)
                crud.create(db, data)
                success_count += 1
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")

        return success_count, errors

    except Exception as e:
        return 0, [f"File error: {str(e)}"]
