"""Utility for json conversion and selenium setup"""

import os
import json
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions


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


def init_driver():
    """Initialize selenium driver

    Returns:
        driver: selenium driver
    """
    options = FirefoxOptions()
    options.add_argument("--headless")

    # print(os.environ.get("SELENIUM_DRIVER"))
    selenium_driver = os.environ.get("SELENIUM_DRIVER")
    driver = webdriver.Firefox(executable_path=selenium_driver, options=options)

    return driver
