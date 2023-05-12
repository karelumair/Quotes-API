"""Utility for scraping quotes data"""


import re
import traceback
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from celery import shared_task, states
from celery.exceptions import Ignore
from selenium.webdriver.common.by import By
from mongoengine.errors import NotUniqueError
from utils.utils import init_driver, get_date
from database.models import ScrapedAuthor, Author, Quote, ScheduledTask
from constants.app_constants import QUOTES_URL
from services.scraper.utils import ScrapingTask, TaskStatus


def update_task_status(
    self, scheduled_task: ScheduledTask, single_page: bool = False
) -> dict:
    """Update Tasks Status based on work completed

    Args:
        scheduled_task (ScheduledTask): Task object to update status for
        single_page (bool): bool to scrape only single page

    Returns:
        dict: dictionary of task statuses
    """
    task_status = ScrapingTask(task=scheduled_task)

    task_status.update(quote=TaskStatus.IN_PROGRESS)
    try:
        quote_status = scrape_quotes(self, single_page=single_page)
        task_status.update(quote=TaskStatus.SUCCESS)
    except Exception:
        quote_status = self.AsyncResult(self.request.id).info
        task_status.update(quote=TaskStatus.FAILED)

    task_status.update(author=TaskStatus.IN_PROGRESS)
    try:
        author_status = scrape_authors(self)
        task_status.update(author=TaskStatus.SUCCESS)
    except Exception:
        author_status = self.AsyncResult(self.request.id).info
        task_status.update(author=TaskStatus.FAILED)

    return {"quotes": quote_status, "authors": author_status}


@shared_task(bind=True)
def scrape_data_scheduler(self, task_id: str) -> dict:
    """This function scrape quotes and authors data as scheduled tasks.

    Args:
        task_id (bool): scheduled task id

    Returns:
        dict: dict of no. of fetched records
    """
    scheduled_task = ScheduledTask.objects.get(id=task_id)
    scheduled_task.update(celeryTask=self.request.id)

    task_status = update_task_status(self, scheduled_task)

    return task_status


@shared_task(bind=True)
def scrape_data(self, single_page: bool = False) -> dict:
    """This function scrape quotes and authors data at a time.

    Args:
        single_page (bool): bool to scrape only single page

    Returns:
        dict: dict of no. of fetched records
    """
    try:
        scraper_task = ScheduledTask(
            celeryTask=self.request.id, description="scrape_data"
        )
        scraper_task.save()
        task_status = update_task_status(self, scraper_task, single_page)
    except Exception as exp_err:
        self.update_state(
            state=states.FAILURE,
            meta={
                "exc_type": type(exp_err).__name__,
                "exc_message": traceback.format_exc().split("\n"),
            },
        )
        raise Ignore() from exp_err

    return task_status


def scrape_quotes(self, single_page: bool) -> dict:
    """This function scrape quotes data

    Args:
        single_page (bool): bool to scrape only single page

    Returns:
        dict: dict of no. of fetched records
    """
    self.update_state(
        state="IN_PROGRESS",
        meta={"scraping": "quotes", "fetched_records": 0},
    )

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
                state="IN_PROGRESS",
                meta={"scraping": "quotes", "fetched_records": fetched_records},
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


def scrape_authors(self) -> dict:
    """This function scrape authors data

    Returns:
        dict: dict of no. of fetched records
    """
    scraped_authors = ScrapedAuthor.objects()
    fetched_records = 0

    self.update_state(
        state="IN_PROGRESS",
        meta={
            "scraping": "authors",
            "fetched_records": 0,
            "total": len(scraped_authors),
        },
    )
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
            meta={
                "scraping": "authors",
                "fetched_records": fetched_records,
                "total": len(scraped_authors),
            },
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
