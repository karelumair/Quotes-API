"""Scraper Utilities"""

from dataclasses import dataclass
from enum import Enum


class TaskStatus(Enum):
    """Possible Task Statuses"""

    NOT_STARTED: str = "NOT_STARTED"
    IN_PROGRESS: str = "IN_PROGRESS"
    FAILED: str = "FAILED"
    SUCCESS: str = "SUCCESS"


@dataclass
class ScrapingTask:
    """Dataclass for Scraping Task Status"""

    quote: str = TaskStatus.NOT_STARTED.value
    author: str = TaskStatus.NOT_STARTED.value
    task: object = None

    def update(self, quote: TaskStatus = None, author: TaskStatus = None) -> None:
        """Update Task Status"""

        if quote:
            self.quote = quote.value
        if author:
            self.author = author.value

        self.task.update(status=self.to_dict())

    def to_dict(self) -> dict:
        """Return dict of task status"""

        return {"quote": self.quote, "author": self.author}
