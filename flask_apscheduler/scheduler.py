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
from apscheduler.util import obj_to_ref, ref_to_obj, undefined
from flask import Flask
from .exceptions import ConfigurationError
from .views import get_job, get_jobs, pause_job, resume_job, run_job, get_scheduler_info

LOGGER = logging.getLogger('flask_apscheduler')


class APScheduler(object):
    """Provides a scheduler integrated to Flask."""

    def __init__(self, scheduler=None, app=None):
        self.__scheduler = scheduler or BackgroundScheduler()
        self.__allowed_hosts = ['*']
        self.__host_name = socket.gethostname().lower()
        self.__views_enabled = False

        if app:
            self.init_app(app)

    @property
    def host_name(self):
        """Gets the host name."""
        return self.__host_name

    @property
    def allowed_hosts(self):
        """Gets the allowed hosts."""
        return self.__allowed_hosts

    @property
    def running(self):
        """Gets true whether the scheduler is running."""
        return self.scheduler.running

    @property
    def scheduler(self):
        """Gets the base scheduler."""
        return self.__scheduler

    def init_app(self, app):
        """Initializes the APScheduler with a Flask application instance."""

        if not isinstance(app, Flask):
            raise TypeError('app must be a Flask application')

        app.apscheduler = self

        self.__load_config(app)
        self.__load_jobs(app)

        if self.__views_enabled:
            self.__load_views(app)

    def start(self):
        """Starts the scheduler."""

        if not self.allowed_hosts:
            LOGGER.debug('No server allowed to start the scheduler.')

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.allowed_hosts)))
            return

        self.__scheduler.start()

    def shutdown(self, wait=True):
        """
        Shuts down the scheduler. Does not interrupt any currently running jobs.

        :param bool wait: ``True`` to wait until all currently executing jobs have finished
        :raises SchedulerNotRunningError: if the scheduler has not been started yet
        """

        self.__scheduler.shutdown(wait)

    def pause_job(self, job_id, jobstore=None):
        """
        Causes the given job not to be executed until it is explicitly resumed.

        :param str|unicode job_id: the identifier of the job
        :param str|unicode jobstore: alias of the job store that contains the job
        """
        self.__scheduler.pause_job(job_id, jobstore)

    def resume_job(self, job_id, jobstore=None):
        """
        Resumes the schedule of the given job, or removes the job if its schedule is finished.

        :param str|unicode job_id: the identifier of the job
        :param str|unicode jobstore: alias of the job store that contains the job
        """
        self.__scheduler.resume_job(job_id, jobstore)

    def run_job(self, job_id, jobstore=None):
        job = self.__scheduler.get_job(job_id, jobstore)

        if not job:
            raise LookupError(job_id)

        job.func(*job.args, **job.kwargs)

    def __load_config(self, app):
        """Loads the configuration from the Flask configuration."""

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

        self.__allowed_hosts = app.config.get('SCHEDULER_ALLOWED_HOSTS', self.__allowed_hosts)
        self.__views_enabled = app.config.get('SCHEDULER_VIEWS_ENABLED', self.__views_enabled)

    def __load_jobs(self, app):
        """Loads the job definitions from the Flask configuration."""

        jobs = app.config.get('SCHEDULER_JOBS')

        if jobs is None:
            jobs = app.config.get('JOBS')

        if jobs:
            for job in jobs:
                self.__load_job(job, app)

    def __load_job(self, job, app):
        """Schedule the specified job."""

        def call_func(*args, **kwargs):
            with app.app_context():
                func(*args, **kwargs)

        id = job.get('id')

        if id is None:
            raise ConfigurationError('Job is missing the parameter id.')

        name = job.get('name') or id

        func = job.get('func')

        if func is None:
            raise ConfigurationError('Job %s is missing the parameter func.' % id)

        if isinstance(func, str):
            func_ref = func
            func = ref_to_obj(func)
        elif callable(func):
            func_ref = obj_to_ref(func)
        else:
            raise ConfigurationError('Job %s has an invalid parameter func.' % id)

        trigger = job.get('trigger')

        if not trigger:
            raise ConfigurationError('Job %s is missing the parameter trigger.' % id)

        job = self.__scheduler.add_job(call_func,
                                       trigger.pop('type', 'date'),
                                       job.get('args'),
                                       job.get('kwargs'),
                                       id,
                                       name,
                                       job.get('misfire_grace_time', undefined),
                                       job.get('coalesce', undefined),
                                       job.get('max_instances', undefined),
                                       job.get('next_run_time', undefined),
                                       job.get('jobstore', 'default'),
                                       job.get('executor', 'default'),
                                       job.get('replace_existing', False),
                                       **trigger)
        job.func_ref = func_ref

    @staticmethod
    def __load_views(app):
        """Adds the routes for the scheduler UI."""

        app.add_url_rule('/scheduler', 'get_scheduler_info', get_scheduler_info)
        app.add_url_rule('/scheduler/jobs', 'get_jobs', get_jobs)
        app.add_url_rule('/scheduler/jobs/<job_id>', 'get_job', get_job)
        app.add_url_rule('/scheduler/jobs/<job_id>/pause', 'pause_job', pause_job)
        app.add_url_rule('/scheduler/jobs/<job_id>/resume', 'resume_job', resume_job)
        app.add_url_rule('/scheduler/jobs/<job_id>/run', 'run_job', run_job)
