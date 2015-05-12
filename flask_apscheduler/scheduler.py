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

"""APScheduler implementation."""

import socket
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.util import obj_to_ref
from apscheduler.util import ref_to_obj
from flask_apscheduler.views import get_job
from flask_apscheduler.views import get_jobs
from flask_apscheduler.views import run_job
from flask_apscheduler.views import get_scheduler_info

LOGGER = logging.getLogger(__name__)


class APScheduler(object):
    """Scheduler that loads the jobs from Flask configuration."""

    def __init__(self, scheduler=None, app=None):
        self.__scheduler = scheduler or BackgroundScheduler()
        self.__allowed_hosts = ['*']
        self.__host_name = socket.gethostname().lower()

        if app:
            self.init_app(app)

    @property
    def host_name(self):
        return self.__host_name

    @property
    def allowed_hosts(self):
        return self.__allowed_hosts

    @property
    def running(self):
        return self.scheduler.running

    @property
    def scheduler(self):
        return self.__scheduler

    def init_app(self, app):
        if not app:
            raise ValueError('app must be a Flask application')

        app.apscheduler = self

        self.__load_config(app)
        self.__load_views(app)

    def start(self):
        if not self.allowed_hosts:
            LOGGER.debug('None server allowed to start the scheduler.')

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.allowed_hosts)))
            return

        self.__scheduler.start()

    def shutdown(self, wait=True):
        self.__scheduler.shutdown(wait)

    def __load_config(self, app):
        options = dict()

        job_stores = app.config.get('SCHEDULER_JOBSTORES')
        if job_stores:
            options['jobstores'] = job_stores

        executors = app.config.get('SCHEDULER_EXECUTORS')
        if executors:
            options['executors'] = executors

        job_defaults = app.config.get('SCHEDULER_JOB_DEFAULTS')
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = app.config.get('SCHEDULER_TIMEZONE')
        if timezone:
            options['timezone'] = timezone

        self.__scheduler.configure(**options)

        jobs = app.config.get('SCHEDULER_JOBS')

        if jobs is None:
            jobs = app.config.get('JOBS')

        for job in jobs:
            self.__load_job(app, job)

        hosts = app.config.get('SCHEDULER_ALLOWED_HOSTS')
        if hosts:
            self.__allowed_hosts = hosts

    def __load_job(self, app, job):
        def call_func(*args, **kwargs):
            with app.app_context():
                func(*args, **kwargs)

        func = job.get('func')
        func_ref = None

        if isinstance(func, str):
            func = ref_to_obj(func)
            func_ref = func

        if callable(func):
            func_ref = obj_to_ref(func)

        id = job.get('id')
        trigger = job.get('trigger')
        func_args = job.get('args')
        func_kwargs = job.get('kwargs')

        trigger_type = trigger.pop('type')

        job = self.__scheduler.add_job(call_func, trigger_type, func_args, func_kwargs, id, **trigger)
        job.func_ref = func_ref

    @staticmethod
    def __load_views(app):
        app.add_url_rule('/scheduler', 'get_scheduler_info', get_scheduler_info)
        app.add_url_rule('/scheduler/jobs', 'get_jobs', get_jobs)
        app.add_url_rule('/scheduler/jobs/<job_id>', 'get_job', get_job)
        app.add_url_rule('/scheduler/jobs/<job_id>/run', 'run_job', run_job)
