import random
import time
from typing import Optional, cast

import cloudscraper
from bs4 import BeautifulSoup, Tag
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_db  # Import session dependency
from app.models import Publication  # Import Publication model

router = APIRouter(
    tags=["Scraper"],
)


def scrape_page(base_url: str, url: str, session: Session) -> Optional[str]:
    """
    Scrapes a single page and inserts data into the database.
    """
    try:
        scraper = cloudscraper.create_scraper()  # Bypass Cloudflare
        response = scraper.get(base_url + url)

        soup = BeautifulSoup(response.text, "html.parser")

        for div in soup.find_all("div", class_="result-container"):
            div = cast(Tag, div)

            title_tag = div.find("h3", class_="title")
            link_tag = div.find("a")
            authors_tags = div.find_all("a", class_="link person")
            year_tag = div.find("span", class_="date")

            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            link = (
                str(link_tag["href"])
                if isinstance(link_tag, Tag) and "href" in link_tag.attrs
                else "No URL"
            )
            authors = (
                [author.text.strip() for author in authors_tags]
                if authors_tags
                else ["No Authors"]
            )
            year = year_tag.text.strip() if year_tag else "No Year"

            # Insert into database
            publication = Publication(
                title=title, link=link, authors=authors, year=year
            )
            session.add(publication)

        session.commit()  # Save all changes

        # Get next page link
        next_tag = soup.find("a", class_="nextLink")
        next_page = (
            str(next_tag["href"])
            if isinstance(next_tag, Tag) and "href" in next_tag.attrs
            else ""
        )

        return next_page

    except Exception as e:
        print(f"Error scraping data: {e}")
        return None


@router.post("/scrape/")
def scrape_publications(
    base_url: str, url: str, session: Session = Depends(get_db)
):
    """
    API endpoint to start scraping.
    """
    while url:
        print(f"Scraping: {url}")
        next_url = scrape_page(base_url, url, session)

        if next_url is None:
            print("No more page to scrape.")
            return

        url = next_url
        time.sleep(random.uniform(1.5, 3))  # Prevent rate-limiting

    return {"message": "Scraping completed successfully!"}
