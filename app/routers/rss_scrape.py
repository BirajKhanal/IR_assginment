import time
from typing import cast

import feedparser
import pandas as pd
import requests
from bs4 import BeautifulSoup, Tag
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlmodel import Session

from app.database import get_db
from app.models import Prediction
from app.services import clean_text, store_scraped_data

router = APIRouter(
    tags=["Task 2"],
)

# RSS Feed URLs
BBC_POLITICS_URL = "https://feeds.bbci.co.uk/news/politics/rss.xml"
BBC_BUSINESS_URL = "https://feeds.bbci.co.uk/news/business/rss.xml"
BBC_HEALTH_URL = "https://feeds.bbci.co.uk/news/health/rss.xml"

CNN_POLITICS_URL = "http://rss.cnn.com/rss/cnn_allpolitics.rss"
CNN_BUSINESS_URL = "http://rss.cnn.com/rss/money_news_international.rss"
CNN_HEALTH_URL = "http://rss.cnn.com/rss/cnn_health.rss"

FOX_POLITICS_URL = "https://moxie.foxnews.com/google-publisher/politics.xml"
FOX_BUSINESS_URL = "https://moxie.foxbusiness.com/google-publisher.xml"
FOX_HEALTH_URL = "https://moxie.foxnews.com/google-publisher/health.xml"

CSV_PATH = "train_data.csv"


def get_full_article(url):
    """Fetch full article content from a given URL"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract full article text
    article_body = soup.find("article")
    article_body = cast(Tag, article_body)
    if not article_body:
        return None

    paragraphs = article_body.find_all("p")
    full_text = "\n".join(p.text for p in paragraphs)

    return full_text.strip()


def load_csv_to_db(file, db):
    # Read CSV into DataFrame
    df = pd.read_csv(file.file)

    # Check if required columns exist
    required_columns = {"content", "category"}
    if not required_columns.issubset(df.columns):
        raise HTTPException(
            status_code=400,
            detail="CSV must contain 'content' and 'category' columns.",
        )

    # Convert DataFrame rows to database objects
    predictions = [
        Prediction(content=str(row["content"]), category=str(row["category"]))
        for _, row in df.iterrows()
    ]

    # Insert into the database
    db.add_all(predictions)
    db.commit()

    return predictions


@router.post("/rss-scrape")
def rss_data(session: Session = Depends(get_db)):
    """Scrape news articles from multiple sources and store them."""
    sources = {
        "Politics": [BBC_POLITICS_URL, CNN_POLITICS_URL, FOX_POLITICS_URL],
        "Business": [BBC_BUSINESS_URL, CNN_BUSINESS_URL, FOX_BUSINESS_URL],
        "Health": [BBC_HEALTH_URL, CNN_HEALTH_URL, FOX_HEALTH_URL],
    }

    documents = []
    per_category_limit = 20

    for category, urls in sources.items():
        count = 0
        for url in urls:
            if count >= per_category_limit:
                break  # Stop if per-category limit is reached
            feed = feedparser.parse(url)
            for entry in feed.entries:
                if count >= per_category_limit:
                    break  # Stop if per-category limit is reached

                full_text = get_full_article(entry.link)
                if full_text:
                    documents.append(
                        {"content": clean_text(full_text), "category": category}
                    )
                    count += 1
                    print(f"✔ Fetched article: {entry.link}")

                time.sleep(1)  # Sleep to avoid getting blocked

    if documents:
        store_scraped_data(session, Prediction, documents)

        # Load CSV data after scraping
        try:
            with open(CSV_PATH, "rb") as csv_file:

                class FakeUploadFile:
                    def __init__(self, file):
                        self.file = file

                csv_file_obj = FakeUploadFile(csv_file)
                load_csv_to_db(csv_file_obj, session)  # Load CSV data

            print("✔ CSV data loaded successfully.")
        except Exception as e:
            print(f"Error loading CSV: {e}")

    return {
        "message": "Scraping completed successfully!",
        "total_records": len(documents),
    }


@router.post("/upload-csv")
async def upload_csv(
    file: UploadFile = File(...), db: Session = Depends(get_db)
):
    """Upload a CSV file and insert its data into the database."""
    try:
        predictions = load_csv_to_db(file, db)

        return {
            "message": "CSV data inserted successfully!",
            "total_records": len(predictions),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
