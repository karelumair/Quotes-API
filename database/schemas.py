"""Schema's for Data Validation"""

AUTHOR_REQUIRED_FIELDS = ["name", "dob", "country", "description"]

AUTHOR_SCHEMA = {
    "type": "object",
    "properties": {
        "name": {"type": "string"},
        "dob": {"type": "string"},
        "country": {"type": "string"},
        "description": {"type": "string"},
    },
}


QUOTE_REQUIRED_FIELDS = ["quote", "tags"]

QUOTE_SCHEMA = {
    "type": "object",
    "properties": {
        "quote": {"type": "string"},
        "author": {"type": "string"},
        "scrapedAuthor": {"type": "string"},
        "tags": {"type": "array"},
    },
}
