from __future__ import absolute_import

import datetime
import flask

from apscheduler.job import Job
from .utils import job_to_dict


def jsonify(data, status=None):
    content = flask.current_app.json.dumps(data, default=_default)
    return flask.current_app.response_class(content, status=status, mimetype="application/json")


def _default(obj):
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    if isinstance(obj, Job):
        return job_to_dict(obj)

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")
