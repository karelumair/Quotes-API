from flask import Response, current_app
from flask_restful import Resource
from database.models import ScrapedAuthor
from database.models import Quote
from utils.scraping import scrapeQuotes
from utils.utils import objectToJson


class ScrapeApi(Resource):
    def get(self):
        """Scrape and add data to the database

        Returns:
            Response: JSON object of message success
        """
        try:
            quotes = scrapeQuotes("https://quotes.toscrape.com/")

            for quote in quotes:
                author = ScrapedAuthor(**quote.pop("author"))
                author.save()

                quote["scrapedAuthor"] = author.id
                quote = Quote(**quote)
                quote.save()

            response, status = {"message": "Data scraping successful!"}, 200
            current_app.logger.info(f"GET Quote {id}")
        except Exception as e:
            response, status = {"Error": str(e)}, 400
            current_app.logger.error(f"Scrape {str(e)}")

        return Response(
            objectToJson(response), mimetype="application/json", status=status
        )
