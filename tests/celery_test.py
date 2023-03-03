"""Celery task Tests"""

import pytest
from app import create_app
from services.scraper.scraper import scrape_data


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
def make_celery(make_app):  # pylint: disable=W0613,W0621
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


def test_scrape_data(make_celery, celery_worker):  # pylint: disable=W0613,W0621
    """Test Case for Scraping Quotes

    Args:
        make_celery (fixture): creates celery app
        celery_worker (fixture): creates celery worker
    """
    assert scrape_data.delay(single_page=True).get() == {
        "quotes": {"fetched_records": 10},
        "authors": {"fetched_records": 8, "total": 8},
    }
