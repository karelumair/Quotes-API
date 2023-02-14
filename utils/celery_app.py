"""Celery App"""

from celery import Celery, Task


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
