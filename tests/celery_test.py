"""Celery task Tests"""

import pytest
from app import create_app
from utils.scraping import scrape_quotes, scrape_authors


@pytest.fixture(scope="session")
def make_app(request):
    """Creates Flask for testing

    Returns:
        Flask: Flask app
    """
    app_ = create_app("test")
    ctx = app_.app_context()
    ctx.push()

    def teardown():
        ctx.pop()

    request.addfinalizer(teardown)
    return app_


@pytest.fixture(scope="session")
def make_celery(make_app):
    """Create celery app for testing

    Args:
        make_app (Flask): Flask app
    """
    # pylint: disable=["import-outside-toplevel", "unused-import"]
    from celery.contrib.testing import (
        tasks,
    )

    celery = make_app.extensions["celery"]

    return celery


def test_scrape_quotes(make_celery, celery_worker):
    """Test Case for Scraping Quotes

    Args:
        make_celery (fixture): creates celery app
        celery_worker (fixture): creates celery worker
    """
    assert scrape_quotes.delay(single_page=True).get() == {"fetched_records": 10}


def test_scrape_authors(make_celery, celery_worker):
    """Test Case for Scraping Authors

    Args:
        make_celery (fixture): creates celery app
        celery_worker (fixture): creates celery worker
    """
    assert scrape_authors.delay().get() == {"fetched_records": 8, "total": 8}
