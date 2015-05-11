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
from flask_apscheduler.utils import import_string

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

        if isinstance(jobs, list):
            for job in jobs:
                self.__load_job(job)

        if isinstance(jobs, dict):
            for id, job in jobs.items():
                self.__load_job(job, id)

        hosts = app.config.get('APSCHEDULER_ALLOWED_HOSTS')
        if hosts:
            for host in hosts:
                self.__hosts.append(host.lower())

    def start(self):
        if not self.__allowed_hosts:
            LOGGER.debug('None server allowed to start the scheduler.')

        if self.host_name not in self.__allowed_hosts and '*' not in self.__allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.__allowed_hosts)))
            return

        self.__scheduler.start()

    def shutdown(self, wait=True):
        self.__scheduler.shutdown(wait)

    def __load_job(self, job, id=None):
        func = job.get('func')

        if not func:
            raise Exception('func is mandatory.')

        if isinstance(func, str):
            func = import_string(func)

        if not hasattr(func, '__call__'):
            raise Exception('func must be a function.')

        trigger = job.get('trigger', 'interval')
        args = job.get('args')
        kwargs = job.get('kwargs')

        trigger_args = dict()

        if trigger == 'interval':
            self.__copy_item('weeks', job, trigger_args)
            self.__copy_item('days', job, trigger_args)
            self.__copy_item('hours', job, trigger_args)
            self.__copy_item('minutes', job, trigger_args)
            self.__copy_item('seconds', job, trigger_args)
            self.__copy_item('start_date', job, trigger_args)
            self.__copy_item('end_date', job, trigger_args)
            self.__copy_item('timezone', job, trigger_args)
        elif trigger == 'cron':
            self.__copy_item('year', job, trigger_args)
            self.__copy_item('month', job, trigger_args)
            self.__copy_item('day', job, trigger_args)
            self.__copy_item('week', job, trigger_args)
            self.__copy_item('day_of_week', job, trigger_args)
            self.__copy_item('hour', job, trigger_args)
            self.__copy_item('minute', job, trigger_args)
            self.__copy_item('second', job, trigger_args)
        elif trigger == 'date':
            self.__copy_item('run_date', job, trigger_args)
            self.__copy_item('timezone', job, trigger_args)
        else:
            raise Exception('Trigger %s is invalid.' % trigger)

        self.__scheduler.add_job(func, trigger, args, kwargs, id, **trigger_args)

    @staticmethod
    def __copy_item(prop, src, dst):
        value = src.get(prop)
        if value:
            dst[prop] = value
