# Copyright 2015 Vinicius Chiele. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

from apscheduler.jobstores.base import JobLookupError
from collections import OrderedDict
from flask import current_app, jsonify, Response
from .utils import job_to_dict


def get_scheduler_info():
    """Gets the scheduler info."""

    scheduler = current_app.apscheduler

    d = OrderedDict([
        ('current_host', scheduler.host_name),
        ('allowed_hosts', scheduler.allowed_hosts),
        ('running', scheduler.running)
    ])

    return Response(json.dumps(d, indent=2), mimetype='application/json')


def get_job(job_id):
    """Gets the specified job."""

    job = current_app.apscheduler.scheduler.get_job(job_id)

    if job:
        return Response(json.dumps(job_to_dict(job), indent=2), mimetype='application/json')

    response = jsonify(message='Job %s not found' % job_id)
    response.status_code = 404

    return response


def get_jobs():
    """Gets all jobs scheduled."""

    jobs = current_app.apscheduler.scheduler.get_jobs()

    job_states = []

    for job in jobs:
        job_states.append(job_to_dict(job))

    return Response(json.dumps(job_states, indent=2), mimetype='application/json')


def pause_job(job_id):
    """Pauses the specified job."""

    job = current_app.apscheduler.scheduler.get_job(job_id)

    try:
        current_app.apscheduler.pause_job(job_id)
        return jsonify(message='Job %s paused' % job.id)
    except JobLookupError:
        response = jsonify(error_message='Job %s not found' % job_id)
        response.status_code = 404
        return response
    except Exception as e:
        response = jsonify(error_message=str(e))
        response.status_code = 500
        return response


def resume_job(job_id):
    """Resumes the specified job."""

    job = current_app.apscheduler.scheduler.get_job(job_id)

    try:
        current_app.apscheduler.resume_job(job_id)
        return jsonify(message='Job %s resumed' % job.id)
    except JobLookupError:
        response = jsonify(error_message='Job %s not found' % job_id)
        response.status_code = 404
        return response
    except Exception as e:
        response = jsonify(error_message=str(e))
        response.status_code = 500
        return response


def run_job(job_id):
    """Executes the specified job."""

    try:
        current_app.apscheduler.run_job(job_id)
        return jsonify(message='Job %s executed' % job_id)
    except LookupError:
        response = jsonify(error_message='Job %s not found' % job_id)
        response.status_code = 404
        return response
    except Exception as e:
        response = jsonify(error_message=str(e))
        response.status_code = 500
        return response
