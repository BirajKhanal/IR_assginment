import time
from typing import cast

import cloudscraper
from bs4 import BeautifulSoup, Tag
from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.database import get_db
from app.models import Publication
from app.services import store_scraped_data

router = APIRouter(
    tags=["Task 1"],
)

BASE_URL = "https://pureportal.coventry.ac.uk"
URLS = [
    "/en/organisations/fbl-school-of-economics-finance-and-accounting/publications/"
]


def scrape_page(base_url: str, url: str):
    """
    Scrapes a single page and inserts data into the database.
    """
    try:
        scraper = cloudscraper.create_scraper()  # Bypass Cloudflare
        response = scraper.get(base_url + url)

        soup = BeautifulSoup(response.text, "html.parser")

        publications = []

        for div in soup.find_all("div", class_="result-container"):
            div = cast(Tag, div)

            title_tag = div.find("h3", class_="title")
            link_tag = div.find("a")
            year_tag = div.find("span", class_="date")
            authors_tags = div.find_all("a", class_="link person")

            title = title_tag.get_text(strip=True) if title_tag else "No Title"
            link = (
                str(link_tag["href"])
                if isinstance(link_tag, Tag) and "href" in link_tag.attrs
                else "No URL"
            )
            year = year_tag.text.strip() if year_tag else "No Year"
            authors = (
                [
                    {
                        "name": author.text.strip(),
                        "link": (
                            str(author["href"])
                            if isinstance(author, Tag)
                            and "href" in author.attrs
                            else ""
                        ),
                    }
                    for author in authors_tags
                ]
                if authors_tags
                else []
            )

            if not authors:
                continue

            publications.append(
                {
                    "title": title,
                    "link": link,
                    "authors": authors,
                    "year": year,
                }
            )

        # Get next page link
        next_tag = soup.find("a", class_="nextLink")
        next_page = (
            str(next_tag["href"])
            if isinstance(next_tag, Tag) and "href" in next_tag.attrs
            else ""
        )

        return publications, next_page

    except Exception as e:
        print(f"Error scraping data: {e}")
        return None, None


@router.post("/scrape")
def scrape_publications(
    base_url: str = BASE_URL,
    url: str = URLS[0],
    session: Session = Depends(get_db),
):
    """
    API endpoint to start scraping.
    """
    all_publications = []

    while url:
        print(f"Scraping: {url}")
        scraped_data, next_url = scrape_page(base_url, url)

        if scraped_data:
            all_publications.extend(scraped_data)

        if next_url is None:
            print("No more page to scrape.")
            return

        url = next_url
        time.sleep(2)  # Prevent rate-limiting

    if all_publications:
        store_scraped_data(
            session, Publication, all_publications, search_field="search_vector"
        )

    return {
        "message": "Scraping completed successfully!",
        "total_records": len(all_publications),
    }
