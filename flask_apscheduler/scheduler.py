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
import functools
import importlib        
import logging
import os
import socket
from logging.handlers import RotatingFileHandler

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import make_response
from . import api
from .utils import fix_job_def, pop_trigger

LOGGER = logging.getLogger('flask_apscheduler')


class APScheduler(object):
    """Provides a scheduler integrated to Flask."""

    def __init__(self, scheduler=None, app=None):
        self._scheduler = scheduler or BackgroundScheduler()
        self._host_name = socket.gethostname().lower()
        self._authentication_callback = None

        self.allowed_hosts = ['*']
        self.auth = None
        self.api_enabled = False
        self.app = None

        if app:
            self.init_app(app)

    @property
    def host_name(self):
        """Get the host name."""
        return self._host_name

    @property
    def running(self):
        """Get true whether the scheduler is running."""
        return self.scheduler.running

    @property
    def scheduler(self):
        """Get the base scheduler."""
        return self._scheduler

    def init_app(self, app):
        """Initialize the APScheduler with a Flask application instance."""

        self.app = app
        self.app.apscheduler = self

        self._load_config()
        if self.api_enabled:
            self._load_api()

    def start(self):
        """Start the scheduler."""

        if self.host_name not in self.allowed_hosts and '*' not in self.allowed_hosts:
            LOGGER.debug('Host name %s is not allowed to start the APScheduler. Servers allowed: %s' %
                         (self.host_name, ','.join(self.allowed_hosts)))
            return

        self._scheduler.start()
        self._load_jobs()

    def shutdown(self, wait=True):
        """
        Shut down the scheduler. Does not interrupt any currently running jobs.

        :param bool wait: ``True`` to wait until all currently executing jobs have finished
        :raises SchedulerNotRunningError: if the scheduler has not been started yet
        """

        self._scheduler.shutdown(wait)

    def add_job(self, id, func, **kwargs):
        """
        Add the given job to the job list and wakes up the scheduler if it's already running.

        :param str id: explicit identifier for the job (for modifying it later)
        :param func: callable (or a textual reference to one) to run at the given time
        """

        job_def = dict(kwargs)
        job_def['id'] = id
        job_def['func'] = func
        job_def['name'] = job_def.get('name') or id

        fix_job_def(job_def)

        return self._scheduler.add_job(**job_def)

    def delete_job(self, id, jobstore=None):
        """
        Remove a job, preventing it from being run any more.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self._scheduler.remove_job(id, jobstore)

    def delete_all_jobs(self, jobstore=None):
        """
        Remove all jobs from the specified job store, or all job stores if none is given.
        
        :param str|unicode jobstore: alias of the job store
        """

        self._scheduler.remove_all_jobs(jobstore)

    def get_job(self, id, jobstore=None):
        """
        Return the Job that matches the given ``id``.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that most likely contains the job
        :return: the Job by the given ID, or ``None`` if it wasn't found
        :rtype: Job
        """

        return self._scheduler.get_job(id, jobstore)

    def get_jobs(self, jobstore=None):
        """
        Return a list of pending jobs (if the scheduler hasn't been started yet) and scheduled jobs, either from a
        specific job store or from all of them.

        :param str jobstore: alias of the job store
        :rtype: list[Job]
        """

        return self._scheduler.get_jobs(jobstore)

    def modify_job(self, id, jobstore=None, **changes):
        """
        Modify the properties of a single job. Modifications are passed to this method as extra keyword arguments.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        fix_job_def(changes)

        if 'trigger' in changes:
            trigger, trigger_args = pop_trigger(changes)
            self._scheduler.reschedule_job(id, jobstore, trigger, **trigger_args)

        return self._scheduler.modify_job(id, jobstore, **changes)

    def pause_job(self, id, jobstore=None):
        """
        Pause the given job until it is explicitly resumed.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """

        self._scheduler.pause_job(id, jobstore)

    def resume_job(self, id, jobstore=None):
        """
        Resume the schedule of the given job, or removes the job if its schedule is finished.

        :param str id: the identifier of the job
        :param str jobstore: alias of the job store that contains the job
        """
        self._scheduler.resume_job(id, jobstore)

    def run_job(self, id, jobstore=None):
        job = self._scheduler.get_job(id, jobstore)

        if not job:
            raise LookupError(id)

        job.func(*job.args, **job.kwargs)

    def authenticate(self, func):
        """
        A decorator that is used to register a function to authenticate a user.
        :param func: The callback to authenticate.
        """
        self._authentication_callback = func
        return func

    def _load_config(self):
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

        self._scheduler.configure(**options)


        self.jobconfig = self.app.config.get('SCHEDULER_JOBCONFIG', None)  # Textual reference to the jobs dictionary.
        self.auth = self.app.config.get('SCHEDULER_AUTH', self.auth)
        self.api_enabled = self.app.config.get('SCHEDULER_VIEWS_ENABLED', self.api_enabled)  # for compatibility reason
        self.api_enabled = self.app.config.get('SCHEDULER_API_ENABLED', self.api_enabled)
        self.allowed_hosts = self.app.config.get('SCHEDULER_ALLOWED_HOSTS', self.allowed_hosts)

    def _load_jobs(self):
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

    def _load_api(self):
        """Add the routes for the scheduler API."""
        self.app.add_url_rule('/scheduler', 'get_scheduler_info', self._apply_auth(api.get_scheduler_info))
        self.app.add_url_rule('/scheduler/jobs', 'add_job', self._apply_auth(api.add_job), methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs', 'get_jobs', self._apply_auth(api.get_jobs))
        self.app.add_url_rule('/scheduler/jobs/reload_jobs', 'reload_jobs', self._apply_auth(api.reload_jobs), methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<job_id>', 'get_job', self._apply_auth(api.get_job))
        self.app.add_url_rule('/scheduler/jobs/<job_id>', 'delete_job', self._apply_auth(api.delete_job), methods=['DELETE'])
        self.app.add_url_rule('/scheduler/jobs/<job_id>', 'update_job', self._apply_auth(api.update_job), methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<id>/reschedule', 'reschedule_job', self._apply_auth(api.reschedule_job), methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<id>/reschedule_once', 'reschedule_job_once', self._apply_auth(api.reschedule_job_once), methods=['PATCH'])
        self.app.add_url_rule('/scheduler/jobs/<job_id>/pause', 'pause_job', self._apply_auth(api.pause_job), methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<job_id>/resume', 'resume_job', self._apply_auth(api.resume_job), methods=['POST'])
        self.app.add_url_rule('/scheduler/jobs/<job_id>/run', 'run_job', self._apply_auth(api.run_job), methods=['POST'])

    def _apply_auth(self, view_func):
        """
        Apply decorator to authenticate the user who is making the request.
        :param view_func: The flask view func.
        """
        @functools.wraps(view_func)
        def decorated(*args, **kwargs):
            if not self.auth:
                return view_func(*args, **kwargs)

            auth_data = self.auth.get_authorization()

            if auth_data is None:
                return self._handle_authentication_error()

            if not self._authentication_callback or not self._authentication_callback(auth_data):
                return self._handle_authentication_error()

            return view_func(*args, **kwargs)

        return decorated

    def _handle_authentication_error(self):
        """
        Return an authentication error.
        """
        response = make_response('Access Denied')
        response.headers['WWW-Authenticate'] = self.auth.get_authenticate_header()
        response.status_code = 401
        return response

    def create_job_loggers(self, jobs):
        """Creates a logger for each job using the job id as logger name.

        Adds a file handler for each job logger. Uses the JOBLOG_PATH from your Flask config class.
        """
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

    def reschedule_job_once(self, id, **data):
        """Reschedules a job once.

        So it runs next time with the given trigger, but the after next run will have again the normal trigger schedule
        as defined in the job definitions. Requires the job definition path in the request body.
        """
        if self.jobconfig:
            jobs = self.loadconfig(self.jobconfig)
        else:
            LOGGER.error("Please provide 'SCHEDULER_JOBCONFIG' in your scheduler configuration.")
            return None            
        self._scheduler.reschedule_job(id, **data)
        modify_kwargs = self.fix_trigger([x for x in jobs if x["id"] == id][0])
        modify_kwargs = self.remove_trigger_kwargs(modify_kwargs)
        modify_kwargs = self.rename_dictkey(modify_kwargs, "id", "job_id")
        self.scheduler.modify_job(**modify_kwargs)

    def get_trigger_kwargs(self, func, trigger, id=None, job_id=None, name=None, coalesce=None, misfire_grace_time=None, max_instances=None, next_run_time=None, **kwargs):
        """Returns trigger kwargs. 

        It'd be better to put the trigger kwargs into a subdictionary though, than extracting them like this.
        """
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

    def loadconfig(self, ref):
        """Returns the job definition dictionary from the given textual reference.

        Example for the textual reference: 'somemodule.somefile.myconfdict'.
        importlib.reload() ensures to reimport each time.
        """
        mod, var = ref.rsplit(".", 1)
        mod = importlib.reload(importlib.import_module(mod))
        jobs = getattr(mod, var)
        return jobs

    def fix_trigger(self, kwargs):
        """Replaces the trigger string value for the triggers 'interval', 'date' and 'cron' with their class instance.

        apscheduler.modify_job() for example wants the trigger as an object and not string.
        """
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

    def reload_jobs(self, jobs=None, reschedule_all=False):
        """Go through all defined jobs and check if they're in the jobstore, if not add them.

        Apply any job definition changes. If reschedule_all is True, then also reschedule all jobs with the current
        defined trigger. Jobstore jobs, that are not in the job definitions are removed.
        """
        if self.jobconfig:
            jobs = self.loadconfig(self.jobconfig)
        elif jobs:
            pass
        else:
            jobconfig_err = "Please provide 'SCHEDULER_JOBCONFIG' in your scheduler configuration."
            LOGGER.error(jobconfig_err)
            return {"error": jobconfig_err}
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
                self.scheduler.modify_job(**modify_kwargs)
                if reschedule_all in ["true", "True"]:
                    self.scheduler.reschedule_job(**reschedule_kwargs)
                LOGGER.debug("Job already in jobstore. Updated possible definitions changes.")
            else:   
                LOGGER.debug("Added schedule for: {0}".format(x["id"]))
                self.scheduler.add_job(**x)
        # Removing job ids that are no longer in our job definitions.
        for x in jobstore_ids:
            if x not in [x["id"] for x in jobs]:
                self.delete_job(x)
        return self.get_jobs()
