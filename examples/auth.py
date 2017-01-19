from flask import Flask
from flask_apscheduler import APScheduler
from flask_apscheduler.auth import HTTPBasicAuth


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

    SCHEDULER_API_ENABLED = True
    SCHEDULER_AUTH = HTTPBasicAuth()


def job1(a, b):
    print(str(a) + ' ' + str(b))


if __name__ == '__main__':
    app = Flask(__name__)
    app.config.from_object(Config())

    scheduler = APScheduler()
    # it is also possible to set the authentication directly
    # scheduler.auth = HTTPBasicAuth()
    scheduler.init_app(app)
    scheduler.start()

    @scheduler.authenticate
    def authenticate(auth):
        return auth['username'] == 'guest' and auth['password'] == 'guest'

    app.run()
