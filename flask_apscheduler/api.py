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

from apscheduler.jobstores.base import ConflictingIdError, JobLookupError
from collections import OrderedDict
from flask import current_app, request, Response
from .json import jsonify


def get_scheduler_info():
    """Gets the scheduler info."""

    scheduler = current_app.apscheduler

    d = OrderedDict([
        ('current_host', scheduler.host_name),
        ('allowed_hosts', scheduler.allowed_hosts),
        ('running', scheduler.running)
    ])

    return jsonify(d)


def add_job():
    """Adds a new job."""

    data = request.get_json(force=True)

    try:
        job = current_app.apscheduler.add_job(**data)
        return jsonify(job)
    except ConflictingIdError:
        return jsonify(dict(error_message='Job %s already exists.' % data.get('id')), status=409)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def delete_job(id):
    """Deletes a job."""

    try:
        current_app.apscheduler.delete_job(id)
        return Response(status=204)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def get_job(id):
    """Gets a job."""

    job = current_app.apscheduler.get_job(id)

    if not job:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)

    return jsonify(job)


def reload_jobs():
    """Reloads all jobs, see flask_apscheduler.APScheduler.reload_jobs()."""
    try:
        return jsonify(current_app.apscheduler.reload_jobs())
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def get_jobs():
    """Gets all scheduled jobs."""

    jobs = current_app.apscheduler.get_jobs()

    job_states = []

    for job in jobs:
        job_states.append(job)

    return jsonify(job_states)


def update_job(id):
    """Updates a job."""

    data = request.get_json(force=True)

    try:
        current_app.apscheduler.modify_job(id, **data)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def reschedule_job(id):
    """Reschedules a job."""

    data = request.get_json(force=True)

    try:
        current_app.apscheduler.scheduler.reschedule_job(id, **data)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def reschedule_job_once(id):
    """Reschedules a job once, so it runs next time with the given trigger, but the after next run will have again
    the normal trigger schedule as defined in the job definitions. Requires the job definition path in the request
    body."""

    data = request.get_json(force=True)

    try:
        current_app.apscheduler.reschedule_job_once(id, **data)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def pause_job(id):
    """Pauses a job."""

    try:
        current_app.apscheduler.pause_job(id)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def resume_job(id):
    """Resumes a job."""

    try:
        current_app.apscheduler.resume_job(id)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except JobLookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)


def run_job(id):
    """Executes a job."""

    try:
        current_app.apscheduler.run_job(id)
        job = current_app.apscheduler.get_job(id)
        return jsonify(job)
    except LookupError:
        return jsonify(dict(error_message='Job %s not found' % id), status=404)
    except Exception as e:
        return jsonify(dict(error_message=str(e)), status=500)
