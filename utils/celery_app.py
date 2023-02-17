"""Celery App"""

from celery import Celery, Task, current_app
from celery.signals import after_task_publish


def init_celery(app) -> Celery:
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


def celery_available():
    """This function checks if the celery worker is running"""

    workers = current_app.control.ping(timeout=1)
    return workers != []
