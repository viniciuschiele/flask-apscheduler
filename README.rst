=================================
Flask-APScheduler
=================================
Flask-APScheduler is a Flask extension which adds support for the APScheduler.

|Version| |Coverage| |CodeClimate| |Travis|

Features
===============
- Loads scheduler configuration from Flask configuration.
- Loads job definitions from Flask configuration.
- Allows to specify the hostname which the scheduler will run on.
- Provides a REST API to manage the scheduled jobs.
- Provides authentication for the REST API.

Installation
===============
You can install Flask-APScheduler via Python Package Index (PyPI_),::

    $ pip install Flask-APScheduler

Documentation
===============

Setup
-----

* Create a flask application. For an example, see `this tutorial <https://pythonspot.com/flask-web-app-with-python/>`_
* Import and initialize ``Flask-APScheduler``
* Set any configuration needed

A basic example will looks like this:

.. code-block:: python
    :linenos:
    from flask import Flask
    # import Flask-APScheduler
    from flask_apscheduler import APScheduler

    # set configuration values
    class Config(object):
        SCHEDULER_API_ENABLED = True

    # create app
    app = Flask(__name__)
    app.config.from_object(Config())

    # initialize scheduler
    scheduler = APScheduler()
    # if you don't wanna use a config, you can set options here:
    # scheduler.api_enabled = True
    scheduler.init_app(app)
    scheduler.start()


    if __name__ == '__main__':
        app.run()

Adding Jobs
-----------

Jobs can be added to the scheduler when the app starts. They are created in decorated functions, which should be imported before ``app.run()`` is called.

.. code-block:: python

    # interval example
    @scheduler.task('interval', id='do_job_1', seconds=30, misfire_grace_time=900)
    def job1():
        print('Job 1 executed')


    # cron examples
    @scheduler.task('cron', id='do_job_2', minute='*')
    def job2():
        print('Job 2 executed')


    @scheduler.task('cron', id='do_job_3', week='*', day_of_week='sun')
    def job3():
        print('Job 3 executed')


If you wish to use anything from your Flask app context inside the job you can use something like this:: python

    def blah():
        with scheduler.app.app_context():
            # do stuff


Logging
-------

API
---

Flask-APScheduler comes with a build-in API. This can be enabled/disabled in your flask configuration.:: python

    SCHEDULER_API_ENABLED: True


/scheduler [GET] > returns basic information about the webapp
/scheduler/jobs [POST json job data] > adds a job to the scheduler
/scheduler/jobs/<job_id> [GET] > returns json of job details
/scheduler/jobs [GET] > returns json with details of all jobs
/scheduler/jobs/<job_id> [DELETE] > deletes job from scheduler
/scheduler/jobs/<job_id> [PATCH json job data] > updates an already existing job
/scheduler/jobs/<job_id>/pause [POST] > pauses a job, returns json of job details
/scheduler/jobs/<job_id>/resume [POST] > resumes a job, returns json of job details
/scheduler/jobs/<job_id>/run [POST] > runs a job now, returns json of job details


Auth
----

Json
----

Scheduler
---------

Configuration
-------------

Configuration options:


`SCHEDULER_API_ENABLED`: True or False
SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite:///flask_context.db')
    }

     JOBS = [
        {
            'id': 'job1',
            'func': show_users,
            'trigger': 'interval',
            'seconds': 2
        }
    ]

     SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url='sqlite://')
    }

    SCHEDULER_EXECUTORS = {
        'default': {'type': 'threadpool', 'max_workers': 20}
    }

    SCHEDULER_JOB_DEFAULTS = {
        'coalesce': False,
        'max_instances': 3
    }

    SCHEDULER_API_ENABLED = True

Tips
----

See `APScheduler's <https://apscheduler.readthedocs.io/en/stable/>`_ documentation for further help.

Take a look at the examples_ to see how it works.

Also take a look at `COMMON-ISSUES.md <https://github.com/viniciuschiele/flask-apscheduler/blob/master/COMMON-ISSUES.md>`_ for help.



Feedback
===============
Please use the Issues_ for feature requests and troubleshooting usage.

.. |Version| image:: https://img.shields.io/pypi/v/flask-apscheduler.svg
   :target: https://pypi.python.org/pypi/Flask-APScheduler

.. |Coverage| image:: https://codecov.io/github/viniciuschiele/flask-apscheduler/coverage.svg
    :target: https://codecov.io/github/viniciuschiele/flask-apscheduler

.. |Travis| image:: https://travis-ci.org/viniciuschiele/flask-apscheduler.svg
    :target: https://travis-ci.org/viniciuschiele/flask-apscheduler

.. |CodeClimate| image:: https://codeclimate.com/github/viniciuschiele/flask-apscheduler/badges/gpa.svg
   :target: https://codeclimate.com/github/viniciuschiele/flask-apscheduler

.. _examples: https://github.com/viniciuschiele/flask-apscheduler/tree/master/examples

.. _PyPi: https://pypi.python.org/pypi/Flask-APScheduler

.. _Issues: https://github.com/viniciuschiele/flask-apscheduler/issues

.. _CommonIssues:

