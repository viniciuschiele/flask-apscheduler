from copy import deepcopy
from flask_apscheduler import utils
from flask import Flask
from unittest import TestCase
from flask_apscheduler.utils import with_app_context

class TestUtils(TestCase):
    def setUp(self):
        self.app = Flask(__name__)
    
    def test_pop_trigger(self):
        def __pop_trigger(trigger, *params):
            data = dict(trigger=trigger)
            next_value = 1

            for param in params:
                data[param] = next_value
                next_value += 1

            trigger_name, trigger_args = utils.pop_trigger(deepcopy(data))
            self.assertEqual(trigger_name, trigger)
            self.assertEqual(len(trigger_args), len(data)-1)
            for key, value in data.items():
                if key != 'trigger':
                    self.assertEqual(trigger_args[key], data[key])

        __pop_trigger('date', 'run_date', 'timezone')
        __pop_trigger('interval', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'start_date', 'end_date', 'timezone')
        __pop_trigger('cron', 'year', 'month', 'day', 'week', 'day_of_week', 'hour', 'minute', 'second', 'start_date', 'end_date', 'timezone')
        self.assertRaises(Exception, utils.pop_trigger, dict(trigger='invalid_trigger'))

    def test_with_app_context(self):
        def one_func():
            return 'x'

        one_func = with_app_context(self.app, one_func)
        self.assertTrue('x' == one_func())
