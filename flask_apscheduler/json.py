import flask
import json

from datetime import datetime
from apscheduler.job import Job
from .utils import job_to_dict


class JSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()

        if isinstance(obj, Job):
            return job_to_dict(obj)

        return super(JSONEncoder, self).default(obj)


def dumps(obj, indent=None):
    return json.dumps(obj, indent=indent, cls=JSONEncoder)


def jsonify(data, status=None):
    indent = None
    if flask.current_app.config['JSONIFY_PRETTYPRINT_REGULAR'] and not flask.request.is_xhr:
        indent = 2
    return flask.current_app.response_class(dumps(data, indent=indent), status=status, mimetype='application/json')
