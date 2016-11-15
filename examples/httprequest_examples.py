"""client.py
# Example with printing the request content
url = "http://localhost:8710/scheduler/jobs/watchdog"
r = requests.Request("PATCH", url, data=json.dumps(data), headers=headers)
prepared = r.prepare()
# Prints the request content (header, url and body)
pretty_print_POST(prepared)
"""
import os
import requests
import json

headers = {'Content-Type': 'application/json'}


def pretty_print_POST(req):
    """At this point it is completely built and ready
    to be fired; it is "prepared".
    However pay attention at the formatting used in 
    this function because it is programmed to be pretty 
    printed and may differ from the actual request.
    """
    print('{}\n{}\n{}\n\n{}'.format(
        '-----------START-----------',
        req.method + ' ' + req.url,
        '\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
        req.body,
    ))


def reload_jobs():
    """Reload all jobs."""
    data = {"configpath": "yourmodule.settings.jobs"}
    url = "http://localhost:8710/scheduler/jobs/reload_jobs"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reload_jobs_and_reschedule():
    """Reload all jobs."""
    data = {"configpath": "yourmodule.settings.jobs", "reschedule_changed_jobs": "True"}
    url = "http://localhost:8710/scheduler/jobs/reload_jobs"
    r = requests.post(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reschedule_job():
    """Reschedule a job"""
    url = "http://localhost:8710/scheduler/jobs/watchdog/reschedule"
    data = {"trigger": "interval", "seconds": 300}
    r = requests.patch(url, data=json.dumps(data), headers=headers)
    print(r.content)


def reschedule_job_once():
    """Reschedule a job"""
    url = "http://localhost:8710/scheduler/jobs/watchdog/reschedule_once"
    data = {"trigger": "interval", "seconds": 300, "configpath": "yourmodule.settings.jobs"}
    r = requests.patch(url, data=json.dumps(data), headers=headers)
    print(r.content)


reload_jobs_and_reschedule()
