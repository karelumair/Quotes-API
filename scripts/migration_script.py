"""Utility for Database Migration"""

import datetime
from database.models import Quote, Author


def get_date(date):
    """convert to datetime object

    Args:
        date (string): date in string

    Returns:
        datetime: datetime object
    """
    return datetime.datetime.strptime(date, "%B %d, %Y")


authors = [
    {
        "name": "Albert Einstein",
        "dob": get_date("March 14, 1879"),
        "country": "Germany",
        "description": "In 1879, Albert Einstein was born in Ulm, Germany. He completed his Ph.D. at the University of Zurich by 1909. His 1905 paper explaining the photoelectric effect, the basis of electronics, earned him the Nobel Prize in 1921. His first paper on Special Relativity Theory, also published in 1905, changed the world. After the rise of the Nazi party, Einstein made Princeton his permanent home, becoming a U.S. citizen in 1940. Einstein, a pacifist during World War I, stayed a firm proponent of social justice and responsibility.",
    },
    {
        "name": "Jane Austen",
        "dob": get_date("December 16, 1775"),
        "country": "United Kingdom",
        "description": "Jane Austen was an English novelist whose works of romantic fiction, set among the landed gentry, earned her a place as one of the most widely read writers in English literature, her realism and biting social commentary cementing her historical importance among scholars and critics.",
    },
    {
        "name": "Steven Martin",
        "dob": get_date("August 14, 1945"),
        "country": "United States",
        "description": "Stephen Glenn 'Steve' Martin is an American actor, comedian, writer, playwright, producer, musician, and composer. He was raised in Southern California in a Baptist family, where his early influences were working at Disneyland and Knott's Berry Farm and working magic and comedy acts at these and other smaller venues in the area.",
    },
    {
        "name": "J.K. Rowling",
        "dob": get_date("July 31, 1965"),
        "country": "United Kingdom",
        "description": "Robert GalbraithAlthough she writes under the pen name J.K. Rowling, pronounced like rolling, her name when her first Harry Potter book was published was simply Joanne Rowling. Anticipating that the target audience of young boys might not want to read a book written by a woman, her publishers demanded that she use two initials, rather than her full name.",
    },
]


def migrate():
    """migrate to database"""
    for author in authors:
        author["createdOn"] = datetime.datetime.utcnow()
        author["createdOn"] = datetime.datetime.utcnow()

        # Creating Author Object
        new_author = Author(**author).save()

        # Adding Author reference to quote
        Quote.objects(quoteBy=author["name"]).update(quoteBy=new_author.id)

    print("Migrated successfully")
