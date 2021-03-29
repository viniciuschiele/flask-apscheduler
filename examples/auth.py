"""Authorization example."""

from flask import Flask

from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth


class Config:
    """App configuration."""

    JOBS = [
        {
            "id": "job1",
            "func": "__main__:job1",
            "args": (1, 2),
            "trigger": "interval",
            "seconds": 10,
        }
    ]

    SCHEDULER_API_ENABLED = True
    SCHEDULER_AUTH = HTTPBasicAuth()


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
    # it is also possible to set the authentication directly
    # scheduler.auth = HTTPBasicAuth()  # noqa: E800
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.authenticate
    def authenticate(auth):
        """Check auth."""
        return auth["username"] == "guest" and auth["password"] == "guest"

    app.run()
