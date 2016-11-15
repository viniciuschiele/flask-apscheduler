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

import importlib        
import logging
import os
import socket
from logging.handlers import RotatingFileHandler

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from . import views
from .utils import fix_job_def, pop_trigger

LOGGER = logging.getLogger('flask_apscheduler')


class APScheduler(object):
    """Provides a scheduler integrated to Flask."""

    def __init__(self, scheduler=None, app=None):
        self.__scheduler = scheduler or BackgroundScheduler()
        self.__allowed_hosts = ['*']
        self.__host_name = socket.gethostname().lower()
        self.__views_enabled = False

        self.app = None

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

        self.app = app
        self.app.apscheduler = self

        self.__load_config()
        if self.__views_enabled:
            self.__load_views()

    def start(self):
        """Starts the scheduler."""

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.allowed_hosts)))
            return

        self.__scheduler.start()
        self.__load_jobs()

    def shutdown(self, wait=True):
        """
        Shuts down the scheduler. Does not interrupt any currently running jobs.

        :param bool wait: ``True`` to wait until all currently executing jobs have finished
        :raises SchedulerNotRunningError: if the scheduler has not been started yet
        """

        self.__scheduler.shutdown(wait)

    def add_job(self, id, func, **kwargs):
        """
        Adds the given job to the job list and wakes up the scheduler if it's already running.

        :param str id: explicit identifier for the job (for modifying it later)
        :param func: callable (or a textual reference to one) to run at the given time
        """

        job_def = dict(kwargs)
        job_def['id'] = id
        job_def['func'] = func
        job_def['name'] = job_def.get('name') or id

        fix_job_def(job_def)

        return self.__scheduler.add_job(**job_def)

    def delete_job(self, id, jobstore=None):
        """
        Removes a job, preventing it from being run any more.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self.__scheduler.remove_job(id, jobstore)

    def delete_all_jobs(self, jobstore=None):
        """
        Removes all jobs from the specified job store, or all job stores if none is given.
        
        :param str|unicode jobstore: alias of the job store
        """

        self.__scheduler.remove_all_jobs(jobstore)

    def get_job(self, id, jobstore=None):
        """
        Returns the Job that matches the given ``id``.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that most likely contains the job
        :return: the Job by the given ID, or ``None`` if it wasn't found
        :rtype: Job
        """

        return self.__scheduler.get_job(id, jobstore)

    def get_jobs(self, jobstore=None):
        """
        Returns a list of pending jobs (if the scheduler hasn't been started yet) and scheduled jobs, either from a
        specific job store or from all of them.

        :param str jobstore: alias of the job store
        :rtype: list[Job]
        """

        return self.__scheduler.get_jobs(jobstore)

    def modify_job(self, id, jobstore=None, **changes):
        """
        Modifies the properties of a single job. Modifications are passed to this method as extra keyword arguments.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        fix_job_def(changes)

        if 'trigger' in changes:
            trigger, trigger_args = pop_trigger(changes)
            self.__scheduler.reschedule_job(id, jobstore, trigger, **trigger_args)

        return self.__scheduler.modify_job(id, jobstore, **changes)

    def pause_job(self, id, jobstore=None):
        """
        Causes the given job not to be executed until it is explicitly resumed.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self.__scheduler.pause_job(id, jobstore)

    def resume_job(self, id, jobstore=None):
        """
        Resumes the schedule of the given job, or removes the job if its schedule is finished.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self.__scheduler.resume_job(id, jobstore)

    def run_job(self, id, jobstore=None):
        job = self.__scheduler.get_job(id, jobstore)

        if not job:
            raise LookupError(id)

        job.func(*job.args, **job.kwargs)

    def __load_config(self):
        """Loads the configuration from the Flask configuration."""

        options = dict()

        job_stores = self.app.config.get('SCHEDULER_JOBSTORES')
        if job_stores:
            options['jobstores'] = job_stores

        executors = self.app.config.get('SCHEDULER_EXECUTORS')
        if executors:
            options['executors'] = executors

        job_defaults = self.app.config.get('SCHEDULER_JOB_DEFAULTS')
        if job_defaults:
            options['job_defaults'] = job_defaults

        timezone = self.app.config.get('SCHEDULER_TIMEZONE')
        if timezone:
            options['timezone'] = timezone

        self.__scheduler.configure(**options)

        self.__allowed_hosts = self.app.config.get('SCHEDULER_ALLOWED_HOSTS', self.__allowed_hosts)
        self.__views_enabled = self.app.config.get('SCHEDULER_VIEWS_ENABLED', self.__views_enabled)

    def __load_jobs(self):
        """Loads the job definitions from the Flask configuration."""

        jobs = self.app.config.get('SCHEDULER_JOBS')
        job_stores = self.app.config.get('SCHEDULER_JOBSTORES')

        if not jobs:
            jobs = self.app.config.get('JOBS')

        if jobs:
            if job_stores:
                self.reload_jobs(jobs=jobs)
            else:
                for job in jobs:
                    self.add_job(**job)

    def create_job_loggers(self, jobs):
        """Creates a logger for each job using the job id as logger name. Adds a file handler for each job logger. Uses
        the JOBLOG_PATH from your Flask config class."""
        self.add_filehandler("apscheduler.executors.default")
        self.add_filehandler("apscheduler.scheduler")
        self.add_filehandler("flask_apscheduler")
        for x in jobs:
            # Creating a logger for each job and adding a seperate filehandler for each logger. Job ids have to have the
            # same logger name of the functions that the jobs invoke.         
            self.add_filehandler(x["id"])

    def add_filehandler(self, name):
        joblog_path = self.app.config.get('JOBLOG_PATH')
        logger = logging.getLogger(name)
        # backupCount keeps old logs, e.g. backupCount=5 would keep app.log, app.log.1, app.log.2, up to app.log.5.
        # maxBytes=5*1024*1024 equals 5 MiB.
        fileh = RotatingFileHandler(os.path.join(joblog_path, "%s.log" % name), mode='a', maxBytes=5*1024*1024,
                                    backupCount=5, encoding=None, delay=0)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fileh.setFormatter(formatter)
        # Removing all old handlers. Requires [:], which takes a copy, because log.handlers removes handlers inplace
        # and then our loop fails. If not removing old handlers we'd get dupes.
        for hdlr in logger.handlers[:]:
            logger.removeHandler(hdlr)
        logger.addHandler(fileh)

    def reschedule_job_once(self, id, configpath, **data):
        """Reschedules a job once, so it runs next time with the given trigger, but the after next run will have again
        the normal trigger schedule as defined in the job definitions. Requires the job definition path in the request
        body."""
        jobs = self.loadconfig(configpath)
        self.__scheduler.reschedule_job(id, **data)
        modify_kwargs = self.fix_trigger([x for x in jobs if x["id"] == id][0])
        modify_kwargs = self.remove_trigger_kwargs(**modify_kwargs)
        modify_kwargs = self.rename_dictkey(modify_kwargs, "id", "job_id")
        self.scheduler.modify_job(**modify_kwargs)

    def get_trigger_kwargs(self, func, trigger, id=None, job_id=None, name=None, coalesce=None, misfire_grace_time=None, max_instances=None, next_run_time=None, **kwargs):
        """Returns trigger kwargs. It'd be better to put the trigger kwargs into a subdictionary though, than extracting
        them like this."""
        if kwargs:
            return kwargs
        else:
            return None

    def remove_trigger_kwargs(self, x):
        """Removes trigger kwargs."""
        kwargs = self.get_trigger_kwargs(**x)
        if kwargs:
            [x.pop(k) for k, v in kwargs.items()]
        return x

    def loadconfig(self, configpath):
        """Returns the job definition dictionary from given configpath. importlib.reload() ensures to reimport each
        time."""
        mod, var = configpath.rsplit(".", 1)
        mod = importlib.reload(importlib.import_module(mod))
        jobs = getattr(mod, var)
        return jobs

    def fix_trigger(self, kwargs):
        """Replaces the trigger string value for the triggers 'interval', 'date' and 'cron' with their actual
        class instance. apscheduler.modify_job() for example wants the trigger as an object and not string."""
        trigger_kwargs = self.get_trigger_kwargs(**kwargs)
        if kwargs["trigger"] == "interval":
            kwargs["trigger"] = apscheduler.triggers.interval.IntervalTrigger(**trigger_kwargs)
        elif kwargs["trigger"] == "date":
            kwargs["trigger"] = apscheduler.triggers.date.DateTrigger(**trigger_kwargs)
        elif kwargs["trigger"] == "cron":
            kwargs["trigger"] = apscheduler.triggers.cron.CronTrigger(**trigger_kwargs)
        return kwargs

    def rename_dictkey(self, kwargs, old, new):
        """Renames the key 'id' to 'job_id'."""
        x = kwargs.copy()
        x[new] = x.pop(old)
        return x

    def reload_jobs(self, configpath=None, jobs=None, reschedule_changed_jobs=False):
        """Goes through all defined jobs and checks if they're in the jobstore, if not they're added. Applies any job
        definition changes. If reschedule_changed_jobs is True, then it also reschedules all jobs with the current
        defined trigger. Jobstore jobs, that are not in our job definitions are removed. 
        Example for the configpath parameter: 'somemodule.somefile.myconfdict'."""
        if configpath:
            jobs = self.loadconfig(configpath)
        elif jobs:
            pass
        else:
            LOGGER.error("Please provide either a configpath or a list with the job definitions.")
            return None
        jobstore_ids = [j.id for j in self.scheduler.get_jobs()]
        joblog_path = self.app.config.get('JOBLOG_PATH')
        if joblog_path:
            self.create_job_loggers(jobs)
        for x in jobs: 
            modify_kwargs = self.rename_dictkey(x, "id", "job_id")
            reschedule_kwargs = self.rename_dictkey(x, "id", "job_id")
            reschedule_kwargs.pop("func")
            if x["id"] in jobstore_ids:
                modify_kwargs = self.fix_trigger(modify_kwargs)
                modify_kwargs = self.remove_trigger_kwargs(modify_kwargs)
                self.scheduler.modify_job(**modify_kwargs)  # "default"
                if reschedule_changed_jobs in ["true", "True"]:
                    self.scheduler.reschedule_job(**reschedule_kwargs)  # jobstore="default"
                LOGGER.debug("Job already in jobstore. Updated possible definitions changes.")
            else:   
                LOGGER.debug("Added schedule for: {0}".format(x["id"]))
                self.scheduler.add_job(**x)
        # Removing job ids that are no longer in our job definitions.
        for x in jobstore_ids:
            if x not in [x["id"] for x in jobs]:
                self.delete_job(x)

    def __load_views(self):
        """Adds the routes for the scheduler UI."""

        self.app.add_url_rule('/scheduler', 'get_scheduler_info', views.get_scheduler_info)
        self.app.add_url_rule('/scheduler/jobs', 'add_job', views.add_job, methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs', 'get_jobs', views.get_jobs)
        self.app.add_url_rule('/scheduler/jobs/reload_jobs', 'reload_jobs', views.reload_jobs, methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<id>', 'get_job', views.get_job)
        self.app.add_url_rule('/scheduler/jobs/<id>', 'delete_job', views.delete_job, methods=['DELETE'])
        self.app.add_url_rule('/scheduler/jobs/<id>', 'update_job', views.update_job, methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<id>/reschedule', 'reschedule_job', views.reschedule_job, methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<id>/reschedule_once', 'reschedule_job_once', views.reschedule_job_once, methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<id>/pause', 'pause_job', views.pause_job, methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<id>/resume', 'resume_job', views.resume_job, methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<id>/run', 'run_job', views.run_job, methods=['POST'])
