"""Example using flask context."""

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask, current_app

from flask_apscheduler import APScheduler


def show_app_name():
    """Print all users."""
    print(f"Running example={current_app.name}")


class Config:
    """App configuration."""

    JOBS = [{"id": "job1", "func": show_app_name, "trigger": "interval", "seconds": 2}]

    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///flask_context.db")
    }

    SCHEDULER_API_ENABLED = True


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run()
