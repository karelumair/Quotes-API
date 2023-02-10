"""All the Scrape API endpoints"""

from flask import Response, current_app
from flask_restful import Resource
from database.models import ScrapedAuthor
from database.models import Quote
from utils.scraping import scrape_quotes
from utils.utils import object_to_json


class ScrapeApi(Resource):
    """API for Scraping"""

    def get(self):
        """Scrape and add data to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            quotes = scrape_quotes("https://quotes.toscrape.com/")

            for quote in quotes:
                author = ScrapedAuthor(**quote.pop("author"))
                author.save()

                quote["scrapedAuthor"] = author.id
                quote = Quote(**quote)
                quote.save()

            response, status = {
                "message": "Data scraping successful!",
                "n_records": len(quotes),
            }, 200
            current_app.logger.info(f"GET Quote {id}")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return Response(
            object_to_json(response), mimetype="application/json", status=status
        )
