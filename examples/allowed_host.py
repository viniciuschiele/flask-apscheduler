from flask import Flask
from flask_apscheduler import APScheduler


class Config(object):
    JOBS = [
        {
            'id': 'job1',
            'func': '__main__:job1',
            'args': (1, 2),
            'trigger': 'interval',
            'seconds': 10
        }
    ]

    SCHEDULER_ALLOWED_HOSTS = ['my_servers_name']
    SCHEDULER_VIEWS_ENABLED = True


def job1(a, b):
    print(str(a) + ' ' + str(b))


app = Flask(__name__)
app.config.from_object(Config())

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

app.run()
