import time
from typing import cast

import feedparser
import requests
from bs4 import BeautifulSoup, Tag
from fastapi import APIRouter

# Scrape articles from RSS
router = APIRouter(
    tags=["Predection"],
)


def get_full_article(url):
    """Fetch full article content from a given URL"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    # BBC articles usually have content inside <article> tags
    article_body = soup.find("article")
    article_body = cast(Tag, article_body)
    if not article_body:
        return None

    paragraphs = article_body.find_all("p")
    full_text = "\n".join(p.text for p in paragraphs)

    return full_text.strip()


@router.get("/task2-rss-data-fetch/")
def predection():
    categories = {
        "Politics": "https://feeds.bbci.co.uk/news/politics/rss.xml",
        "Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "Health": "https://feeds.bbci.co.uk/news/health/rss.xml",
    }

    documents = []

    for category, url in categories.items():
        feed = feedparser.parse(url)
        for entry in feed.entries:
            full_text = get_full_article(entry.link)
            if full_text:
                documents.append({"text": full_text, "category": category})
                print(f"✔ Fetched article: {entry.link}")

            time.sleep(1)  # Sleep to avoid getting blocked

    return {"data": documents}
