import html
import re

from sqlalchemy.sql import text
from sqlmodel import Session, SQLModel, delete


def store_scraped_data(
    session: Session,
    table: type[SQLModel],
    data: list[dict],
    search_field: str = "",
):
    """
    Clears the table and inserts the given data to avoid duplicates.

    Args:
        session (Session): The database session.
        table (SQLModel): The SQLModel class representing the table.
        data (list[dict]): List of dictionaries containing the new data.
        search_field (str, optional): The column name to update as a search vector.
    """
    # Delete all existing records
    session.exec(delete(table))  # pyright: ignore

    # Insert new records
    new_records = [table(**item) for item in data]
    session.add_all(new_records)
    session.commit()

    # Update search vector if field is provided
    if search_field:
        session.exec(
            text(
                f"UPDATE {table.__tablename__} SET {search_field} = to_tsvector('english', title)"
            )  # pyright: ignore
        )
        session.commit()


def clean_text(text: str) -> str:
    text = html.unescape(text)  # Convert &quot; &amp; etc. to normal characters
    text = text.replace("\n", " ")  # Remove newlines
    text = re.sub(r"\s+", " ", text).strip()  # Normalize spaces
    return text
