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
    def scheduler(self):
        return self.__scheduler

    def init_app(self, app):
        if not app:
            raise ValueError('app must be a Flask application')

        app.apscheduler = self

        self.__load_config(app)
        self.__load_views(app)

    def get_job(self, job_id):
        return self.__scheduler.get_job(job_id)

    def get_jobs(self):
        return self.__scheduler.get_jobs()

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

        job_stores = app.config.get('APSCHEDULER_JOBSTORES')
        if job_stores:
            options['jobstores'] = job_stores

        executors = app.config.get('APSCHEDULER_EXECUTORS')
        if executors:
            options['executors'] = executors

        job_defaults = app.config.get('APSCHEDULER_JOB_DEFAULTS')
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = app.config.get('APSCHEDULER_TIMEZONE')
        if timezone:
            options['timezone'] = timezone

        self.__scheduler.configure(**options)

        jobs = app.config.get('APSCHEDULER_JOBS')

        for job in jobs:
            self.__load_job(app, job)

        hosts = app.config.get('APSCHEDULER_ALLOWED_HOSTS')
        if hosts:
            for host in hosts:
                self.__allowed_hosts.append(host.lower())

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

        trigger_args = dict()
        trigger_type = trigger.get('type')

        if trigger_type == 'interval':
            self.__copy_item('weeks', trigger, trigger_args)
            self.__copy_item('days', trigger, trigger_args)
            self.__copy_item('hours', trigger, trigger_args)
            self.__copy_item('minutes', trigger, trigger_args)
            self.__copy_item('seconds', trigger, trigger_args)
            self.__copy_item('start_date', trigger, trigger_args)
            self.__copy_item('end_date', trigger, trigger_args)
            self.__copy_item('timezone', trigger, trigger_args)
        elif trigger_type == 'cron':
            self.__copy_item('year', trigger, trigger_args)
            self.__copy_item('month', trigger, trigger_args)
            self.__copy_item('day', trigger, trigger_args)
            self.__copy_item('week', trigger, trigger_args)
            self.__copy_item('day_of_week', trigger, trigger_args)
            self.__copy_item('hour', trigger, trigger_args)
            self.__copy_item('minute', trigger, trigger_args)
            self.__copy_item('second', trigger, trigger_args)
        elif trigger_type == 'date':
            self.__copy_item('run_date', trigger, trigger_args)
            self.__copy_item('timezone', trigger, trigger_args)
        else:
            raise Exception('Trigger %s is invalid.' % trigger)

        job = self.__scheduler.add_job(call_func, trigger_type, func_args, func_kwargs, id, **trigger_args)
        job.func_ref = func_ref

    @staticmethod
    def __load_views(app):
        app.add_url_rule('/jobs', 'get_jobs', get_jobs)
        app.add_url_rule('/jobs/<job_id>', 'get_job', get_job)
        app.add_url_rule('/jobs/<job_id>/run', 'run_job', run_job)

    @staticmethod
    def __copy_item(prop, src, dst):
        value = src.get(prop)
        if value:
            dst[prop] = value
