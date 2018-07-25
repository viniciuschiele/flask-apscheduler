import base64
import json

from werkzeug.routing import BuildError
from flask import Flask, url_for
from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth
from unittest import TestCase


class TestAPI(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()
        self.scheduler.api_enabled = True
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.client = self.app.test_client()

    def test_scheduler_info(self):
        response = self.client.get(self.scheduler.api_prefix)
        self.assertEqual(response.status_code, 200)
        info = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(info['current_host'])
        self.assertEqual(info['allowed_hosts'], ['*'])
        self.assertTrue(info['running'])

    def test_add_job(self):
        job = {
            'id': 'job1',
            'func': 'tests.test_api:job1',
            'trigger': 'date',
            'run_date': '2020-12-01T12:30:01+00:00',
        }

        response = self.client.post(self.scheduler.api_prefix + '/jobs', data=json.dumps(job))
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('run_date'), job2.get('run_date'))

    def test_add_conflicted_job(self):
        job = {
            'id': 'job1',
            'func': 'tests.test_api:job1',
            'trigger': 'date',
            'run_date': '2020-12-01T12:30:01+00:00',
        }

        response = self.client.post(self.scheduler.api_prefix + '/jobs', data=json.dumps(job))
        self.assertEqual(response.status_code, 200)

        response = self.client.post(self.scheduler.api_prefix + '/jobs', data=json.dumps(job))
        self.assertEqual(response.status_code, 409)

    def test_add_invalid_job(self):
        job = {
            'id': None,
        }

        response = self.client.post(self.scheduler.api_prefix + '/jobs', data=json.dumps(job))
        self.assertEqual(response.status_code, 500)

    def test_delete_job(self):
        self.__add_job()

        response = self.client.delete(self.scheduler.api_prefix + '/jobs/job1')
        self.assertEqual(response.status_code, 204)

        response = self.client.get(self.scheduler.api_prefix + '/jobs/job1')
        self.assertEqual(response.status_code, 404)

    def test_delete_job_not_found(self):
        response = self.client.delete(self.scheduler.api_prefix + '/jobs/job1')
        self.assertEqual(response.status_code, 404)

    def test_get_job(self):
        job = self.__add_job()

        response = self.client.get(self.scheduler.api_prefix + '/jobs/job1')
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('minutes'), job2.get('minutes'))

    def test_get_job_not_found(self):
        response = self.client.get(self.scheduler.api_prefix + '/jobs/job1')
        self.assertEqual(response.status_code, 404)

    def test_get_all_jobs(self):
        job = self.__add_job()

        response = self.client.get(self.scheduler.api_prefix + '/jobs')
        self.assertEqual(response.status_code, 200)

        jobs = json.loads(response.get_data(as_text=True))

        self.assertEqual(len(jobs), 1)

        job2 = jobs[0]

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(job.get('trigger'), job2.get('trigger'))
        self.assertEqual(job.get('minutes'), job2.get('minutes'))

    def test_update_job(self):
        job = self.__add_job()

        data_to_update = {
            'args': [1],
            'trigger': 'cron',
            'minute': '*/1',
            'start_date': '2021-01-01'
        }

        response = self.client.patch(self.scheduler.api_prefix + '/jobs/job1', data=json.dumps(data_to_update))
        self.assertEqual(response.status_code, 200)

        job2 = json.loads(response.get_data(as_text=True))

        self.assertEqual(job.get('id'), job2.get('id'))
        self.assertEqual(job.get('func'), job2.get('func'))
        self.assertEqual(data_to_update.get('args'), job2.get('args'))
        self.assertEqual(data_to_update.get('trigger'), job2.get('trigger'))
        self.assertEqual('2021-01-01T00:00:00+00:00', job2.get('start_date'))
        self.assertEqual('2021-01-01T00:00:00+00:00', job2.get('next_run_time'))

    def test_update_job_not_found(self):
        data_to_update = {
            'args': [1],
            'trigger': 'cron',
            'minute': '*/1',
            'start_date': '2021-01-01'
        }

        response = self.client.patch(self.scheduler.api_prefix + '/jobs/job1', data=json.dumps(data_to_update))
        self.assertEqual(response.status_code, 404)

    def test_update_invalid_job(self):
        self.__add_job()

        data_to_update = {
            'trigger': 'invalid_trigger',
        }

        response = self.client.patch(self.scheduler.api_prefix + '/jobs/job1', data=json.dumps(data_to_update))
        self.assertEqual(response.status_code, 500)

    def test_pause_and_resume_job(self):
        self.__add_job()

        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/pause')
        self.assertEqual(response.status_code, 200)
        job = json.loads(response.get_data(as_text=True))
        self.assertIsNone(job.get('next_run_time'))

        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/resume')
        self.assertEqual(response.status_code, 200)
        job = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(job.get('next_run_time'))

    def test_pause_and_resume_job_not_found(self):
        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/pause')
        self.assertEqual(response.status_code, 404)

        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/resume')
        self.assertEqual(response.status_code, 404)

    def test_run_job(self):
        self.__add_job()

        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/run')
        self.assertEqual(response.status_code, 200)
        job = json.loads(response.get_data(as_text=True))
        self.assertIsNotNone(job.get('next_run_time'))

    def test_run_job_not_found(self):
        response = self.client.post(self.scheduler.api_prefix + '/jobs/job1/run')
        self.assertEqual(response.status_code, 404)

    def __add_job(self):
        job = {
            'id': 'job1',
            'func': 'tests.test_api:job1',
            'trigger': 'interval',
            'minutes': 10,
        }

        response = self.client.post(self.scheduler.api_prefix + '/jobs', data=json.dumps(job))
        return json.loads(response.get_data(as_text=True))


class TestAPIPrefix(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()
        self.scheduler.api_enabled = True
        self.scheduler.api_prefix = '/api'
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.client = self.app.test_client()

    def test_api_prefix(self):
        response = self.client.get(self.scheduler.api_prefix + '/jobs')
        self.assertEqual(response.status_code, 200)

    def test_invalid_api_prefix(self):
        response = self.client.get('/invalidapi/jobs')
        self.assertEqual(response.status_code, 404)


class TestEndpointPrefix(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()
        self.scheduler.api_enabled = True
        self.scheduler.endpoint_prefix = 'api.'
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.client = self.app.test_client()

    def test_endpoint_prefix(self):
        with self.scheduler.app.test_request_context():
            valid_url = True if url_for(self.scheduler.endpoint_prefix + 'get_scheduler_info') else False
            self.assertTrue(valid_url)

    def test_invalid_endpoint_prefix(self):
        with self.scheduler.app.test_request_context():
            try:
                valid_url = url_for('get_scheduler_info')
            except BuildError as _:
                valid_url = False
            self.assertFalse(valid_url)


class TestHTTPBasicAuth(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.scheduler = APScheduler()
        self.scheduler.auth = HTTPBasicAuth()
        self.scheduler.api_enabled = True
        self.scheduler.init_app(self.app)
        self.scheduler.start()
        self.scheduler.authenticate(self._authenticate)
        self.client = self.app.test_client()

    def _authenticate(self, auth):
        return auth['username'] == 'test' and auth['password'] == 'test'

    def test_valid_credentials(self):
        headers = {'Authorization': 'Basic ' + base64.b64encode(b'test:test').decode('ascii')}
        response = self.client.get(self.scheduler.api_prefix + '', headers=headers)
        self.assertEqual(response.status_code, 200)

    def test_invalid_credentials(self):
        headers = {'Authorization': 'Basic ' + base64.b64encode(b'guest:guest').decode('ascii')}
        response = self.client.get(self.scheduler.api_prefix + '', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['WWW-Authenticate'], 'Basic realm="Authentication Required"')

    def test_invalid_header_format(self):
        headers = {'Authorization': 'Basic 1231234'}
        response = self.client.get(self.scheduler.api_prefix + '', headers=headers)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['WWW-Authenticate'], 'Basic realm="Authentication Required"')

    def test_missing_credentials(self):
        response = self.client.get(self.scheduler.api_prefix + '')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers['WWW-Authenticate'], 'Basic realm="Authentication Required"')


def job1(x=0):
    print(x)
