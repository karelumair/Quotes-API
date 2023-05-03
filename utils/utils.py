"""Utility for json conversion and selenium setup"""

import datetime
from selenium import webdriver
from flask_mongoengine import BaseQuerySet
from pymongo.command_cursor import CommandCursor


def cursor_to_json(data: BaseQuerySet) -> list:
    """converts mongo cursor to list of json objects

    Args:
        data (cursor): mongo cursor

    Returns:
        list: list of json objects
    """
    data = [doc.to_json() for doc in data]
    return data


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
        doc["author"]["id"] = str(doc["author"].pop("_id"))
        doc["author"].pop("createdBy")
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
