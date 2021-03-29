"""Example using flask context."""

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from flask_apscheduler import APScheduler

db = SQLAlchemy()


class User(db.Model):
    """User model."""

    id = db.Column(db.Integer, primary_key=True)  # noqa: A003, VNE003
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)


def show_users():
    """Print all users."""
    with db.app.app_context():
        print(User.query.all())


class Config:
    """App configuration."""

    JOBS = [{"id": "job1", "func": show_users, "trigger": "interval", "seconds": 2}]

    SCHEDULER_JOBSTORES = {
        "default": SQLAlchemyJobStore(url="sqlite:///flask_context.db")
    }

    SCHEDULER_API_ENABLED = True


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config())

    db.app = app
    db.init_app(app)

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run()
