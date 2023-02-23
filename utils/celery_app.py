"""Celery App"""

from functools import wraps
from flask import Flask
from celery import Celery, Task, current_app
from celery.signals import after_task_publish


def init_celery(app: Flask) -> Celery:
    """Intialize Celery App"""

    class FlaskTask(Task):
        """FlaskTask Class"""

        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    celery_app.config_from_object(app.config["CELERY"])
    app.extensions["celery"] = celery_app
    celery_app.set_default()
    return celery_app


@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    """Changes the task state, helping to indentify non-existing tasks"""

    task = current_app.tasks.get(sender)
    backend = task.backend if task else current_app.backend

    backend.store_result(headers["id"], None, "IN_PROGRESS")


def check_celery_available(func):
    """This decorator checks if the celery worker is running"""

    @wraps(func)
    def decorated_function(*args, **kwargs):
        workers = current_app.control.ping(timeout=1)
        if workers == []:
            response, status = {"message": "Celery worker is not running!"}, 500
            return response, status

        return func(*args, **kwargs)

    return decorated_function
