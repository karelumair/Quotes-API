"""All the Scrape API endpoints"""

from flask import Response, current_app
from flask_restful import Resource
from database.models import ScrapedAuthor, Quote
from utils.scraping import scrape_quotes, scrape_author
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
            scraped_authors = ScrapedAuthor.objects()

            for author in scraped_authors:
                author_data = scrape_author(author.link)
                author.update(**author_data)

            response, status = {
                "message": "Author Data updated successfully",
                "n_records": len(scraped_authors),
            }, 200
            current_app.logger.info("GET Scrape Authors")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"Scrape {str(exp_err)}")

        return Response(
            object_to_json(response), mimetype="application/json", status=status
        )
