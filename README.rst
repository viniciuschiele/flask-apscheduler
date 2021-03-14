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

    pip install Flask-APScheduler

Documentation
===============

Setup
-----

* Create a flask application. For an example, see `this tutorial <https://pythonspot.com/flask-web-app-with-python/>`_
* Import and initialize ``Flask-APScheduler``
* Set any configuration needed

A basic example will looks like this.

.. code-block:: python

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


Jobs can also be added after you app is running

.. code-block:: python

    scheduler.add_job(**args)

If you wish to use anything from your Flask app context inside the job you can use something like this

.. code-block:: python

    def blah():
        with scheduler.app.app_context():
            # do stuff

Logging
-------

All scheduler events can be used to trigger logging functions. See `APScheduler <https://apscheduler.readthedocs.io/en/stable/userguide.html#scheduler-events>`_ for a list of available events.

If you are using your Flask app context inside of a function triggered by a scheduler event can include something like this

.. code-block:: python

    def blah():
        with scheduler.app.app_context():
            # do stuff

    scheduler.add_listener(blah, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)


API
---

Flask-APScheduler comes with a build-in API. This can be enabled/disabled in your flask configuration.

.. code-block:: python

    SCHEDULER_API_ENABLED: True


- /scheduler [GET] > returns basic information about the webapp
- /scheduler/jobs [POST json job data] > adds a job to the scheduler
- /scheduler/jobs/<job_id> [GET] > returns json of job details
- /scheduler/jobs [GET] > returns json with details of all jobs
- /scheduler/jobs/<job_id> [DELETE] > deletes job from scheduler
- /scheduler/jobs/<job_id> [PATCH json job data] > updates an already existing job
- /scheduler/jobs/<job_id>/pause [POST] > pauses a job, returns json of job details
- /scheduler/jobs/<job_id>/resume [POST] > resumes a job, returns json of job details
- /scheduler/jobs/<job_id>/run [POST] > runs a job now, returns json of job details


Scheduler
---------

Other commands can be passed to the scheduler and are rather self explainatory:

- scheduler.start()
- scheduler.shutdown()
- scheduler.pause() > stops any job from starting. Already running jobs not affected.
- scheduler.resume() > allows scheduled jobs to begin running.
- scheduler.add_listener(<callback function>,<event>)
- scheduler.remove_listener(<callback function>)
- scheduler.add_job(<id>,<function>, **kwargs)
- scheduler.remove_job(<id>, **<jobstore>)
- scheduler.remove_all_jobs(**<jobstore>)
- scheduler.get_job(<id>,**<jobstore>)
- scheduler.modify_job(<id>,**<jobstore>, **kwargs)
- scheduler.pause_job(<id>, **<jobstore>)
- scheduler.resume_job(<id>, **<jobstore>)
- scheduler.run_job(<id>, **<jobstore>)
- scheduler.authenticate(<function>)


Configuration
-------------

Configuration options specific to ``Flask-APScheduler``:

.. code-block:: python

    SCHEDULER_API_ENABLED: <True or False>

Other configuration options are included from `APScheduler <https://apscheduler.readthedocs.io/en/stable/userguide.html#configuring-the-scheduler>`_


Tips
----

When running Flask-APScheduler on a wsgi process only **1** worker should be enabled. APScheduler 3.0 will only work with a single worker process. Jobstores cannot be shared among multiple schedulers.

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

