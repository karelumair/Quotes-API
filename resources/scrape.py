"""All the Scrape API endpoints"""

from flask import make_response, jsonify, current_app
from flask_restful import Resource
from celery.result import AsyncResult
from utils.scraping import scrape_quotes, scrape_authors
from utils.celery_app import celery_available
from constants.app_constants import QUOTES_URL


class ScrapeQuotesApi(Resource):
    """API for Scraping Quotes"""

    def get(self):
        """Scrape and add data to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            if celery_available():
                task = scrape_quotes.delay(QUOTES_URL)

                response, status = {
                    "message": "Scraping task started!",
                    "task_id": task.id,
                }, 200
                current_app.logger.info("GET Scrape Quotes")

            else:
                response, status = {"message": "Celery worker is not running!"}, 500
                current_app.logger.info("GET Scrape Authors: Celery worker not running")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return make_response(jsonify(response), status)


class ScrapeAuthorsApi(Resource):
    """API for Scraping Authors"""

    def get(self):
        """Scrape authors and update to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            if celery_available():
                task = scrape_authors.delay()

                response, status = {
                    "message": "Scraping task started!",
                    "task_id": task.id,
                }, 200
                current_app.logger.info("GET Scrape Authors")

            else:
                response, status = {"message": "Celery worker is not running!"}, 500
                current_app.logger.info("GET Scrape Authors: Celery worker not running")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return make_response(jsonify(response), status)


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
        result = {"task_status": "Task id does not exists"}
        if task_result.status != "PENDING":
            result = {
                "task_status": task_result.status,
            }
        return make_response(jsonify(result), 200)
