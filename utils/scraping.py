"""Utility for scraping quotes data"""


from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from celery import shared_task
from selenium.webdriver.common.by import By
from utils.utils import init_driver, get_date
from database.models import ScrapedAuthor, Author, Quote


@shared_task
def scrape_quotes(url) -> bool:
    """This function scrape quotes data

    Args:
        url (str): link of the website to be scraped

    Returns:
        list: list of quotes data scraped
    """
    driver = init_driver()
    driver.get(url)

    quotes_data = []
    next_page = True

    while next_page:

        for quote_div in driver.find_elements(By.CLASS_NAME, "quote"):
            quote = quote_div.find_element(By.CLASS_NAME, "text").text
            author_name = quote_div.find_element(By.CLASS_NAME, "author").text
            author_link = quote_div.find_element(By.TAG_NAME, "a").get_attribute("href")
            tags = [tag.text for tag in quote_div.find_elements(By.CLASS_NAME, "tag")]
            data = {
                "quote": quote,
                "author": {"name": author_name, "link": author_link},
                "tags": tags,
            }

            quotes_data.append(data)

        try:
            next_li = driver.find_element(By.CLASS_NAME, "next")
            next_page = True

            a_link = next_li.find_element(By.TAG_NAME, "a")
            a_link.click()
        except Exception:
            next_page = False

    driver.quit()
    add_quotes_db(quotes_data)

    return True


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
        quote = Quote(**quote)
        quote.save()

    return True


@shared_task
def scrape_authors() -> bool:
    """This function scrape authors data

    Args:
        url (str): link of the website to be scraped

    Returns:
        bool: returns status true
    """
    for author in ScrapedAuthor.objects():
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

    update_authors_collection()

    return True


def update_authors_collection():
    """This function moves scarped authors to authors collection"""

    for scraped_author in ScrapedAuthor.objects():
        scraped_author_data = scraped_author.to_mongo()
        _id = scraped_author_data.pop("_id")
        scraped_author_data.pop("link")

        author = Author(**scraped_author_data, scrapeId=_id)
        author.save()

        for quote in Quote.objects(scrapedAuthor=_id):
            quote.update(author=author.id, updatedOn=datetime.now(timezone.utc))

    return True
