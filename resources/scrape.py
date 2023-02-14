"""All the Scrape API endpoints"""

from flask import Response, current_app
from flask_restful import Resource
from celery.result import AsyncResult
from database.models import ScrapedAuthor, Quote
from utils.scraping import scrape_quotes, scrape_authors
from utils.utils import object_to_json
from constants.app_constants import QUOTES_URL


class ScrapeQuotesApi(Resource):
    """API for Scraping Quotes"""

    def get(self):
        """Scrape and add data to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            quotes = scrape_quotes(QUOTES_URL)

            for quote in quotes:
                author_data = quote.pop("author")
                author = ScrapedAuthor.objects(link=author_data["link"]).first()

                if author is None:
                    author = ScrapedAuthor(**author_data)
                    author.save()

                quote["scrapedAuthor"] = author.id
                quote = Quote(**quote)
                quote.save()

            response, status = {
                "message": "Data scraping successful!",
                "n_records": len(quotes),
            }, 200
            current_app.logger.info("GET Scrape Quotes")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return Response(
            object_to_json(response), mimetype="application/json", status=status
        )


class ScrapeAuthorsApi(Resource):
    """API for Scraping Authors"""

    def get(self):
        """Scrape authors and update to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            task = scrape_authors.delay()

            response, status = {
                "message": "Scraping task started!",
                "task_id": task.id,
            }, 200
            current_app.logger.info("GET Scrape Authors")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return Response(
            object_to_json(response), mimetype="application/json", status=status
        )


class ScrapeStatus(Resource):
    """Returns status of background task (scraping)"""

    def get(self, task_id: str):
        """Returns task status

        Args:
            task_id (str): id of the task to get status

        Returns:
            tuple: JSON and status code
        """
        task_result = AsyncResult(task_id)
        result = {
            "task_status": task_result.status,
        }
        return result, 200
