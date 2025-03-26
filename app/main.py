from contextlib import asynccontextmanager

import httpx
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.database import create_db_and_tables
from app.routers import classifier, rss_scrape, scrape, search, train


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Creating database tables...")
    create_db_and_tables()
    print("Database tables created.")
    yield


app = FastAPI(lifespan=lifespan)

templates = Jinja2Templates(directory="app/templates")

# HTTP client for scraping requests
http_client = httpx.AsyncClient()

# Background scheduler setup
scheduler = BackgroundScheduler()


# Scrape job triggered by scheduler
@scheduler.scheduled_job("cron", day=1, hour=0, minute=0, second=0)
async def monthly_scrape_job():
    """Triggers /scrape endpoint once a month."""
    async with http_client as client:
        response = await client.get("http://127.0.0.1:8000/scrape")
        print(
            "Scrape triggered!"
            if response.status_code == 200
            else f"Error: {response.status_code}"
        )


# Start the scheduler
scheduler.start()


app.include_router(scrape.router)
app.include_router(search.router)
app.include_router(rss_scrape.router)
app.include_router(train.router)
app.include_router(classifier.router)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def home_page(request: Request):
    """Renders the main home page with Task 1 and Task 2 buttons."""
    return templates.TemplateResponse("home.html", {"request": request})
