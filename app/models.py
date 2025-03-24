from typing import Annotated, Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.orm import mapped_column
from sqlmodel import Field, Index, SQLModel


class Publication(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    link: str
    authors: List[Dict["str", "str"]] = Field(
        sa_column=Column(JSONB)
    )  # Store as JSON
    year: Optional[str] = None
    search_vector: Annotated[
        Optional[str],
        mapped_column(TSVECTOR, nullable=False, server_default="''"),
    ]

    __table_args__ = (
        Index(
            "publication_search_idx", "search_vector", postgresql_using="gin"
        ),
    )

    model_config = {"arbitrary_types_allowed": True}  # pyright: ignore


class Prediction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str
    category: str
