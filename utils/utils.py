"""Utility for json conversion and selenium setup"""

from dataclasses import dataclass
from enum import Enum
import datetime
import json
from selenium import webdriver
from flask_mongoengine import BaseQuerySet
from pymongo.command_cursor import CommandCursor


class TaskStatus(Enum):
    """Possible Task Statuses"""

    NOT_STARTED: str = "NOT_STARTED"
    IN_PROGRESS: str = "IN_PROGRESS"
    FAILED: str = "FAILED"
    SUCCESS: str = "SUCCESS"


@dataclass
class ScrapingTask:
    """Dataclass for Scraping Task Status"""

    quote: str = TaskStatus.NOT_STARTED.value
    author: str = TaskStatus.NOT_STARTED.value
    task: object = None

    def update(self, quote: TaskStatus = None, author: TaskStatus = None) -> None:
        """Update Task Status"""

        if quote:
            self.quote = quote.value
        if author:
            self.author = author.value

        self.task.update(status=self.to_dict())

    def to_dict(self) -> dict:
        """Return dict of task status"""

        return {"quote": self.quote, "author": self.author}


def cursor_to_json(data: BaseQuerySet) -> list:
    """converts mongo cursor to list of json objects

    Args:
        data (cursor): mongo cursor

    Returns:
        list: list of json objects
    """
    data = [doc.to_json() for doc in data]
    return data


def object_to_json(obj):
    """converts model object to json object

    Args:
        data (object): python model object

    Returns:
        json: json object
    """
    return json.dumps(obj, default=str)


def get_date(date: str) -> datetime.datetime:
    """convert to datetime object

    Args:
        date (string): date in string

    Returns:
        datetime: datetime object
    """
    return datetime.datetime.strptime(date, "%B %d, %Y")


def quote_aggregate_to_json(cursor: CommandCursor) -> list:
    """converts quotes aggregation result to json

    Args:
        cursor: mongoengine aggregation result cursor

    Returns:
        list: list of dictionary
    """
    quotes = []

    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        doc["author"]["_id"] = str(doc["author"]["_id"])
        quotes.append(doc)

    return quotes


def init_driver() -> webdriver.Chrome:
    """Initialize selenium driver

    Returns:
        driver: selenium driver
    """
    options = webdriver.ChromeOptions()
    # Using scraper in docker, may lead to weird errors pop-up,
    # such as: Running as root without --no-sandbox is not supported.
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    return webdriver.Chrome(options=options)
