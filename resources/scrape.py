"""All the Scrape API endpoints"""

from flask import make_response, jsonify, current_app, request
from flask_restful import Resource
from flask_jwt_extended import jwt_required
from celery import states
from celery.result import AsyncResult
from database.models import ScheduledTask
from services.scraper.scraper import scrape_data
from utils.celery_app import check_celery_available
from utils.rate_limiter import limiter
from utils.utils import cursor_to_json
from constants.app_constants import SCRAPER_RATE_LIMIT


class ScrapeDataApi(Resource):
    """API for Scraping Quotes"""

    @jwt_required()
    @check_celery_available
    @limiter.limit(SCRAPER_RATE_LIMIT)
    def get(self):
        """Scrape and add data to the database

        Returns:
            Response: JSON object of message success
        """
        current_app.logger.info("GET Scrape Data - REQUEST RECEIVED")

        try:
            task = scrape_data.delay()

            response, status = {
                "message": "Scraping task started!",
                "task_id": task.id,
            }, 200
            current_app.logger.info(f"GET Scrape Data - Task Id: {task.id}")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"GET Scrape Data - {str(exp_err)}")

        return make_response(jsonify(response), status)


class ScrapeStatus(Resource):
    """Returns status of background task (scraping)"""

    @jwt_required()
    def get(self, task_id: str):
        """Returns task status

        Args:
            task_id (str): id of the task to get status

        Returns:
            tuple: JSON and status code
        """
        current_app.logger.info("GET Scrape Status - REQUEST RECEIVED")

        task_result = AsyncResult(task_id)
        result = {"task_status": "Task id does not exists"}

        if task_result.status == states.FAILURE:
            return {"task_status": "FAILED"}

        if task_result.status != states.PENDING:
            result["task_status"] = task_result.status
            result |= task_result.result

        current_app.logger.info(f"GET Scrape Status - Status: {task_result.status}")
        return make_response(jsonify(result), 200)


class ScraperTasks(Resource):
    """Returns status of background task (scraping)"""

    @jwt_required()
    def get(self):
        """Returns task status

        Args:
            task_id (str): id of the task to get status

        Returns:
            tuple: JSON and status code
        """
        current_app.logger.info("GET Scrape Tasks - REQUEST RECEIVED")

        task_type = request.args.get("type", "scrape_data")
        cursor = ScheduledTask.objects(description=task_type).order_by("-createdOn")
        tasks = cursor_to_json(cursor)

        current_app.logger.info(f"GET Scrape Tasks - FETCHED {len(tasks)} Tasks")
        return make_response(jsonify(tasks), 200)
