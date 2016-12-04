"""httprequest_examples.py"""
import json
import os
import requests

headers = {'Content-Type': 'application/json'}


def pretty_print_POST(req):
    """Print request header pretty."""
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def reload_jobs():
    """Reload all jobs."""
    url = "http://localhost:8710/scheduler/jobs/reload_jobs"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reload_jobs_and_reschedule():
    """Reload all jobs and reschedule all jobs."""
    data = {"reschedule_changed_jobs": "True"}
    url = "http://localhost:8710/scheduler/jobs/reload_jobs"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reschedule_job():
    """Reschedule given job."""
    url = "http://localhost:8710/scheduler/jobs/watchdog/reschedule"
    data = {"trigger": "interval", "seconds": 300}
    r = requests.patch(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reschedule_job_once():
    """Reschedule given job once."""
    url = "http://localhost:8710/scheduler/jobs/watchdog/reschedule_once"
    data = {"trigger": "interval", "seconds": 300}
    r = requests.patch(url, data=json.dumps(data), headers=headers)
    print(r.content)


reload_jobs_and_reschedule()
