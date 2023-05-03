"""All the Statistics API endpoints"""

from flask import current_app, make_response, jsonify
from flask_restful import Resource
from database.models import Quote, Author


def get_query_most_popular(field, top_n):
    """Returns Query to get top_n items with given field"""

    return [
        {"$project": {field: 1}},
        {"$unwind": f"${field}"},
        {"$group": {"_id": f"${field}", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": top_n},
    ]


class StatsApi(Resource):
    """All the Statistics API endpoints"""

    def get(self):
        """Get Statistics for Quotes, Authors and Tags"""

        try:
            top_tags_query = get_query_most_popular("tags", 10)
            tag_cursor = Quote.objects(author__exists=True).aggregate(top_tags_query)
            current_app.logger.info("GET Stats - FETCHED TOP Tags")

            top_author_query = get_query_most_popular("author", 1)
            author_cursor = list(
                Quote.objects(author__exists=True).aggregate(top_author_query)
            )
            current_app.logger.info("GET Stats - FETCHED TOP Author")

            top_tags = [tag["_id"] for tag in tag_cursor]

            top_author = Author.objects.get(id=author_cursor[0]["_id"])
            author_tags = Quote.objects(author=author_cursor[0]["_id"]).aggregate(
                top_tags_query
            )
            tags_by_author = [tag["_id"] for tag in author_tags]

            total_quotes = Quote.objects(author__exists=True).count()
            total_authors = Author.objects.count()

            response, status = {
                "top_tags": top_tags,
                "top_author": {
                    "name": top_author.name,
                    "total_quotes": author_cursor[0]["count"],
                    "top_tags": tags_by_author,
                },
                "total_quotes": total_quotes,
                "total_author": total_authors,
            }, 200
            current_app.logger.info("GET Stats - FETCHED ALL Stats")
        except Exception as exp_err:
            response, status = {"Error": str(exp_err)}, 400
            current_app.logger.error(f"GET Stats - {str(exp_err)}")

        return make_response(jsonify(response), status)
