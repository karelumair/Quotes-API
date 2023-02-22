"""Utility for scraping quotes data"""


import re
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from selenium.webdriver.common.by import By
from mongoengine.errors import NotUniqueError
from utils.utils import init_driver, get_date
from database.models import ScrapedAuthor, Author, Quote
from constants.app_constants import QUOTES_URL


@shared_task(bind=True)
def scrape_quotes(self, single_page: bool = False) -> dict:
    """This function scrape quotes data

    Args:
        url (str): link of the website to be scraped

    Returns:
        list: list of quotes data scraped
    """
    driver = init_driver()
    driver.get(QUOTES_URL)

    quotes_data = []
    next_page = True
    fetched_records = 0

    while next_page:

        for quote_div in driver.find_elements(By.CLASS_NAME, "quote"):
            quote = quote_div.find_element(By.CLASS_NAME, "text")
            # This removes html quotes (“ ”) to get only text of the quote.
            # The function replaces quote(“”) characters with empty character.
            # For example. “This is quote” will result to "This is quote"
            quote = re.sub(r"[\“\”]", "", quote.text)

            author_name = quote_div.find_element(By.CLASS_NAME, "author").text
            author_link = quote_div.find_element(By.TAG_NAME, "a").get_attribute("href")
            tags = [tag.text for tag in quote_div.find_elements(By.CLASS_NAME, "tag")]
            data = {
                "quote": quote,
                "author": {"name": author_name, "link": author_link},
                "tags": tags,
            }

            quotes_data.append(data)
            fetched_records += 1
            self.update_state(
                state="IN_PROGRESS", meta={"fetched_records": fetched_records}
            )

        try:
            next_li = driver.find_element(By.CLASS_NAME, "next")
            next_page = not single_page

            a_link = next_li.find_element(By.TAG_NAME, "a")
            a_link.click()
        except Exception:
            next_page = False

    driver.quit()
    add_quotes_db(quotes_data)

    return {"fetched_records": fetched_records}


def add_quotes_db(quotes: list) -> bool:
    """This functions add the quotes documents to the database

    Args:
        quotes (list): List of quotes documents
    """

    for quote in quotes:
        author_data = quote.pop("author")
        author = ScrapedAuthor.objects(link=author_data["link"]).first()

        if author is None:
            author = ScrapedAuthor(**author_data)
            author.save()

        quote["scrapedAuthor"] = author.id
        try:
            quote_obj = Quote(**quote, createdBy="scraper")
            quote_obj.save()
        except NotUniqueError:
            quote_obj = Quote.objects.get(quote=quote["quote"])
            quote_obj.update(
                **quote, updatedOn=datetime.now(timezone.utc), updatedBy="scraper"
            )

    return True


@shared_task(bind=True)
def scrape_authors(self) -> dict:
    """This function scrape authors data

    Args:
        url (str): link of the website to be scraped

    Returns:
        bool: returns status true
    """
    scraped_authors = ScrapedAuthor.objects()
    fetched_records = 0

    for author in scraped_authors:
        res = requests.get(author.link, timeout=10)
        soup = BeautifulSoup(res.content, features="html5lib")

        dob = soup.find(class_="author-born-date").text
        country = soup.find(class_="author-born-location").text[3:]
        description = soup.find(class_="author-description").text.strip()

        author_data = {
            "dob": get_date(dob),
            "country": country,
            "description": description,
        }

        author.update(**author_data, updatedOn=datetime.now(timezone.utc))

        fetched_records += 1
        self.update_state(
            state="IN_PROGRESS",
            meta={"fetched_records": fetched_records, "total": len(scraped_authors)},
        )

    update_authors_collection()

    return {"fetched_records": fetched_records, "total": len(scraped_authors)}


def update_authors_collection() -> bool:
    """This function moves scarped authors to authors collection"""

    for scraped_author in ScrapedAuthor.objects():
        scraped_author_data = scraped_author.to_mongo()
        _id = scraped_author_data.pop("_id")
        scraped_author_data.pop("link")

        try:
            author = Author(**scraped_author_data, scrapeId=_id, createdBy="scraper")
            author.save()
        except NotUniqueError:
            author = Author.objects.get(name=scraped_author_data["name"])
            scraped_author_data["updatedOn"] = datetime.now(timezone.utc)
            scraped_author_data["updatedBy"] = "scraper"
            author.update(**scraped_author_data)

        for quote in Quote.objects(scrapedAuthor=_id):
            quote.update(author=author.id, updatedOn=datetime.now(timezone.utc))

    return True
