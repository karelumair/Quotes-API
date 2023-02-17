"""Utility for json conversion and selenium setup"""

from os import path
import datetime
import json
from selenium import webdriver


def cursor_to_json(data):
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


def get_date(date):
    """convert to datetime object

    Args:
        date (string): date in string

    Returns:
        datetime: datetime object
    """
    return datetime.datetime.strptime(date, "%B %d, %Y")


def init_driver():
    """Initialize selenium driver

    Returns:
        driver: selenium driver
    """
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    return webdriver.Chrome(
        executable_path=path.abspath("chromedriver"), options=options
    )
