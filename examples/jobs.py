"""Basic Flask Example."""


from flask import Flask

from flask_apscheduler import APScheduler


class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job1",
            "func": "jobs:job1",
            "args": (1, 2),
            "trigger": "interval",
            "seconds": 10,
        }
    ]

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
    # it is also possible to enable the API directly
    # scheduler.api_enabled = True  # noqa: E800
    scheduler.init_app(app)
    scheduler.start()

    app.run()
