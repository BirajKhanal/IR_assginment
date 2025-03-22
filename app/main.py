from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import prediction, scrape, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created.")
    yield


# app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)
app = FastAPI(lifespan=lifespan)

app.include_router(scrape.router)
app.include_router(search.router)
app.include_router(prediction.router)
