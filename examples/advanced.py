"""Advanced example using other configuration options."""

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask

from flask_apscheduler import APScheduler


class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job1",
            "func": "advanced:job1",
            "args": (1, 2),
            "trigger": "interval",
            "seconds": 10,
        }
    ]

    SCHEDULER_JOBSTORES = {"default": SQLAlchemyJobStore(url="sqlite://")}

    SCHEDULER_EXECUTORS = {"default": {"type": "threadpool", "max_workers": 20}}

    SCHEDULER_JOB_DEFAULTS = {"coalesce": False, "max_instances": 3}

    SCHEDULER_API_ENABLED = True


def job1(var_one, var_two):
    """Demo job function.

    :param var_two:
    :param var_two:
    """
    print(str(var_one) + " " + str(var_two))


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.start()

    app.run()
