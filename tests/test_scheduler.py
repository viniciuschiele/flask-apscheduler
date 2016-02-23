from flask import Flask
from flask_apscheduler import APScheduler
from unittest import TestCase


class TestScheduler(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()

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
                'func': 'tests.test_views:job1',
                'trigger': 'interval',
                'seconds': 10
            }
        ]

        self.scheduler.init_app(self.app)
        job = self.scheduler.get_job('job1')
        self.assertIsNotNone(job)


def job1():
    pass
