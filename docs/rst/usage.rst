*****************
Basic Application
*****************

Setup
-----

* Create a flask application. For an example, see `this tutorial <https://pythonspot.com/flask-web-app-with-python/>`_
* Import and initialize ``Flask-APScheduler``
* Set any configuration needed

A basic example will looks like this.

.. code-block:: python

    from flask import Flask
    from flask_apscheduler import APScheduler

    # set configuration values
    class Config:
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


    scheduler.start()


Jobs can also be added after you app is running

.. code-block:: python

    scheduler.start()
    scheduler.add_job(**args)


Flask Context
-------------

If you wish to use anything from your Flask app context inside the job you can use something like this

.. code-block:: python

    def blah():
        with scheduler.app.app_context():
            # do stuff
