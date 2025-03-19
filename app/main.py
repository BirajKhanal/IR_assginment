from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routers import scrape


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created.")
    yield


app = FastAPI(lifespan=lifespan)

BASE_URL = "https://pureportal.coventry.ac.uk"
URLS = [
    "/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"
]

app.include_router(scrape.router)
