"""Utility for scraping quotes data"""

from selenium.webdriver.common.by import By
from utils.utils import init_driver


def scrape_quotes(url) -> list:
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
            tags = []

            for tag in quote_div.find_elements(By.CLASS_NAME, "tag"):
                tags.append(tag.text)

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
    return quotes_data