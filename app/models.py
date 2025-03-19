from typing import List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSON
from sqlmodel import Field, SQLModel


class Publication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str
    authors: List[str] = Field(sa_column=Column(JSON))  # Store as JSON
    year: Optional[str] = None
    search_vector: Optional[str] = Field(
        default=None, index=True
    )  # For Full-Text Search
