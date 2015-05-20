from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask import Flask
from flask_apscheduler import APScheduler

class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:job1',
            'args': (1, 2),
            'trigger': {
                'type': 'cron',
                'second': 10
            }
        }
    ]

    APSCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite://')
    }

    APSCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }


def job1(a, b):
    print(str(a) + ' ' + str(b))

app = Flask(__name__)
app.config.from_object(Config())
app.debug = True

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.run()
