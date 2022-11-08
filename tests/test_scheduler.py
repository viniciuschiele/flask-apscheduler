from flask import Flask, current_app
from flask_apscheduler import APScheduler, utils
from unittest import TestCase
import apscheduler
from pytz import utc
import datetime
import sys
import importlib


class TestScheduler(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()
        self.scheduler_two = APScheduler(app=self.app)

    def test_running(self):
        self.assertFalse(self.scheduler.running)
        self.scheduler.start()
        self.assertTrue(self.scheduler.running)

    def test_start_with_allowed_hosts(self):
        self.app.config['SCHEDULER_ALLOWED_HOSTS'] = ['any_server_name']
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertFalse(self.scheduler.running)

    def test_start_without_allowed_hosts(self):
        self.app.config['SCHEDULER_ALLOWED_HOSTS'] = []
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertFalse(self.scheduler.running)

    def test_shutdown(self):
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertTrue(self.scheduler.running)
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_load_jobs_from_config(self):
        self.app.config['JOBS'] = [
            {
                'id': 'job1',
                'func': 'tests.test_api:job1',
                'trigger': 'interval',
                'seconds': 10,
            }
        ]
        self.app.config['SCHEDULER_JOBSTORES'] = {"default": apscheduler.jobstores.memory.MemoryJobStore()}
        self.app.config['SCHEDULER_EXECUTORS'] = {"default": {"type": "threadpool"}}
        self.app.config['SCHEDULER_JOB_DEFAULTS'] = {"coalesce": True}
        self.app.config['SCHEDULER_TIMEZONE'] = utc

        self.scheduler.init_app(app=self.app)
        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)

    def test_task_decorator(self):
        @self.scheduler.task('interval', seconds=10, id='job1')
        def decorated_job():
            pass

        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)


    def test_state_prop(self):
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertTrue(self.scheduler.state)
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.state)

    def test_scheduler_prop(self):
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertIsNotNone(self.scheduler.scheduler)
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_pause_resume(self):
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertTrue(self.scheduler.running)
        self.scheduler.pause()
        self.assertTrue(self.scheduler.state == 2)
        self.scheduler.resume()
        self.assertTrue(self.scheduler.state == 1)
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_add_listener(self):
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.assertTrue(self.scheduler.running)
        self.scheduler.add_listener(None)
        self.scheduler.remove_listener(None)
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_add_remove_job(self):
        @self.scheduler.task('interval', seconds=10, id='job1')
        def decorated_job():
            pass

        self.scheduler.init_app(self.app)
        self.scheduler.start()
        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)

        self.scheduler.remove_job('job1')
        self.assertFalse(self.scheduler.get_job('job1'))
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_add_delete_job(self):
        @self.scheduler.task('interval', seconds=10, id='job1')
        def decorated_job():
            pass

        self.scheduler.init_app(self.app)
        self.scheduler.start()
        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)

        self.scheduler.delete_job('job1')
        self.assertFalse(self.scheduler.get_job('job1'))
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)


    def test_add_remove_all_jobs(self):
        @self.scheduler.task('interval', hours=1, id='job1')
        def decorated_job():
            pass

        @self.scheduler.task('interval', hours=1, id='job2')
        def decorated_job2():
            pass

        self.scheduler.init_app(self.app)
        self.scheduler.start()
        jobs = self.scheduler.get_jobs()
        self.assertTrue(len(jobs) == 2)
        self.scheduler.remove_all_jobs()

        self.assertFalse(self.scheduler.get_job('job1'))
        self.assertFalse(self.scheduler.get_job('job2'))

        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_add_delete_all_jobs(self):
        @self.scheduler.task('interval', hours=1, id='job1')
        def decorated_job():
            pass

        @self.scheduler.task('interval', hours=1, id='job2')
        def decorated_job2():
            pass

        self.scheduler.init_app(self.app)
        self.scheduler.start()
        jobs = self.scheduler.get_jobs()
        self.assertTrue(len(jobs) == 2)
        self.scheduler.delete_all_jobs()

        self.assertFalse(self.scheduler.get_job('job1'))
        self.assertFalse(self.scheduler.get_job('job2'))

        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_job_to_dict(self):
        @self.scheduler.task('interval', hours=1, id='job1', end_date=datetime.datetime.now(), weeks=1, days=1, seconds=99)
        def decorated_job():
            pass
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)

        self.assertTrue(len(utils.job_to_dict(job)))
        self.scheduler.delete_job('job1')
        self.assertFalse(self.scheduler.get_job('job1'))
        self.scheduler.shutdown()
        self.assertFalse(self.scheduler.running)

    def test_run_job(self):
        job = self.scheduler.add_job('job2', job2)

        with self.assertRaises(RuntimeError):
            self.scheduler.run_job('job2')

        job = self.scheduler_two.add_job('job2', job2)
        self.scheduler_two.run_job('job2')

    def test_apply_app_context(self):
        now = datetime.datetime.now(utc)
        self.scheduler_two.start()
        job = self.scheduler_two.add_job('appctx', job2, trigger='date', next_run_time=now)
        executor = self.scheduler_two._scheduler._executors['default']

        self.assertTrue(executor.submit_job(job, [now]) is None)


def job1():
    pass


def job2():
    return current_app.name
