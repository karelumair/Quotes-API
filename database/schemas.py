"""Schema's for Data Validation"""

from typing import Optional
from bson import ObjectId
from pydantic import BaseModel, root_validator


class MongoObjectId(ObjectId):
    """ObjectId Field for Pydantic validation"""

    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, _id):
        """Validates the MongoDB ObjectId"""

        if not ObjectId.is_valid(_id):
            raise ValueError("Invalid objectid")
        return ObjectId(_id)


class AuthorSchema(BaseModel):
    """Pydantic Schema for Author Model"""

    name: str
    dob: str
    country: str
    description: str


class AuthorUpdateSchema(BaseModel):
    """Pydantic Schema for updating Author"""

    name: Optional[str]
    dob: Optional[str]
    country: Optional[str]
    description: Optional[str]


class QuoteSchema(BaseModel):
    """Pydantic Schema for Quote Model"""

    quote: str
    author: Optional[MongoObjectId]
    scrapedAuthor: Optional[MongoObjectId]
    tags: list

    @root_validator(pre=True)
    @classmethod
    def check_author_or_scraped_author(cls, values):
        """Check if document contains either author or scrapedAuthor"""

        if not (values.get("author") or values.get("scrapedAuthor")):
            raise ValueError("Quote must have either an author or scraped author")
        return values


class QuoteUpdateSchema(BaseModel):
    """Pydantic schema for updating Quote"""

    quote: Optional[str]
    tags: Optional[list]
