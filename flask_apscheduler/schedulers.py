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


import socket

from apscheduler.schedulers.background import BackgroundScheduler
from flask_apscheduler.utils import import_string


class APScheduler(object):
    def __init__(self, scheduler=None, app=None):
        self.__scheduler = scheduler or BackgroundScheduler()
        self.__app = app
        self.__servers = None

        if app:
            self.init_app(app)

    @property
    def scheduler(self):
        return self.__scheduler

    def init_app(self, app):
        self.__app = app

        options = dict()

        jobstores = self.__app.config.get('APSCHEDULER_JOBSTORES')
        if jobstores:
            options['jobstores'] = jobstores

        executors = self.__app.config.get('APSCHEDULER_EXECUTORS')
        if executors:
            options['executors'] = executors

        job_defaults = self.__app.config.get('APSCHEDULER_JOB_DEFAULTS')
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = self.__app.config.get('APSCHEDULER_TIMEZONE')
        if timezone:
            options['timezone'] = timezone

        self.__scheduler.configure(**options)

        jobs = self.__app.config.get('APSCHEDULER_JOBS')

        if isinstance(jobs, list):
            for job in jobs:
                self.__load_job(job)

        if isinstance(jobs, dict):
            for id, job in jobs.items():
                self.__load_job(job, id)

        servers = self.__app.config.get('APSCHEDULER_SERVERS')
        if servers:
            self.__servers = []
            for server in servers:
                self.__servers.append(server.lower())

    def start(self):
        if self.__servers:
            server_name = socket.gethostname().lower()
            if server_name not in self.__servers:
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
