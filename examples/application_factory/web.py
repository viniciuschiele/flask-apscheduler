"""Example web view for application factory."""


from flask import Blueprint

from .extensions import scheduler
from .tasks import task2

web_bp = Blueprint("web_bp", __name__)


@web_bp.route("/")
def index():
    """Say hi!.

    :url: /
    :returns: hi!
    """
    return "hi!"


@web_bp.route("/add")
def add():
    """Add a task.

    :url: /add/
    :returns: job
    """
    job = scheduler.add_job(
        func=task2,
        trigger="interval",
        seconds=10,
        id="test job 2",
        name="test job 2",
        replace_existing=True,
    )
    return "%s added!" % job.name
