"""Example of decorators."""
from flask import Flask

from flask_apscheduler import APScheduler


class Config:
    """App configuration."""

    SCHEDULER_API_ENABLED = True


scheduler = APScheduler()


# interval examples
@scheduler.task("interval", id="do_job_1", seconds=30, misfire_grace_time=900)
def job1():
    """Sample job 1."""
    print("Job 1 executed")


# cron examples
@scheduler.task("cron", id="do_job_2", minute="*")
def job2():
    """Sample job 2."""
    print("Job 2 executed")


@scheduler.task("cron", id="do_job_3", week="*", day_of_week="sun")
def job3():
    """Sample job 3."""
    print("Job 3 executed")


if __name__ == "__main__":
    app = Flask(__name__)
    app.config.from_object(Config())

    # it is also possible to enable the API directly
    # scheduler.api_enabled = True  # noqa: E800
    scheduler.init_app(app)
    scheduler.start()

    app.run()
