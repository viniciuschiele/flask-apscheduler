import json

from flask import current_app as app
from flask import jsonify
from flask import Response
from flask_apscheduler.utils import job_to_dict


def get_job(job_id):
    job = app.apscheduler.get_job(job_id)

    if job:
        return Response(json.dumps(job_to_dict(job), indent=2), mimetype='application/json')

    return jsonify(message='Job %s not found' % job_id)


def get_jobs():
    jobs = app.apscheduler.get_jobs()

    job_states = []

    for job in jobs:
        job_states.append(job_to_dict(job))

    return Response(json.dumps(job_states, indent=2), mimetype='application/json')


def run_job(job_id):
    job = app.apscheduler.get_job(job_id)

    if not job:
        response = jsonify(error_message='Job %s not found' % job_id)
        response.status_code = 500
        return response

    try:
        job.func(*job.args, **job.kwargs)
        return jsonify(message='Job %s executed' % job.id)
    except Exception as e:
        response = jsonify(error_message=str(e))
        response.status_code = 500
        return response
