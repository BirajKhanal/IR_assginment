import time

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import cast, func, select
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Publication

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/task1/", response_class=HTMLResponse)
def search_publications(
    request: Request,
    query: str = Query("", alias="query", description="Search query"),
    db: Session = Depends(get_db),
):
    start_time = time.time()
    # Format query for `to_tsquery`
    formatted_query = " | ".join(
        query.split()
    )  # Converts "word1 word2" → "word1 | word2"

    # Explicitly cast `search_vector` to `TSVECTOR`
    search_vector_casted = cast(Publication.search_vector, TSVECTOR)

    stmt = (
        select(
            Publication,
            func.ts_rank(
                search_vector_casted,
                func.to_tsquery("english", formatted_query),
            ).label("rank"),
        )
        .where(
            search_vector_casted.op("@@")(
                func.to_tsquery("english", formatted_query)
            )
        )
        .order_by(
            func.ts_rank(
                search_vector_casted,
                func.to_tsquery("english", formatted_query),
            ).desc()
        )
    )

    results = db.execute(stmt).all()

    search_time = time.time() - start_time
    total_results = len(results)

    results = [
        {
            "title": row[0].title,
            "authors": row[0].authors,
            "link": row[0].link,
            "year": row[0].year,
            "rank": row[1],
        }
        for row in results
    ]

    return templates.TemplateResponse(
        "search.html",
        {
            "request": request,
            "query": query,
            "results": results,
            "search_time": search_time,
            "total_results": total_results,
        },
    )
