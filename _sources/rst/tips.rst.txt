****
Tips & Troubleshooting
****


When running Flask-APScheduler on a wsgi process only **1** worker should be enabled. APScheduler 3.0 will only work with a single worker process. Jobstores cannot be shared among multiple schedulers.

See `APScheduler's <https://apscheduler.readthedocs.io/en/stable/>`_ documentation for further help.

Take a look at the :doc:`examples` to see how it works.

Environment Variables
#####################

Flask-Appscheduler will start a scheduler when running with an environment variable of `FLASK_DEBUG=true` and using flask's werkzeug server OR when running with `FLASK_DEBUG=false` and a production server (gunicorn etc). If you have server details coded directly into the app you can use a pattern like this to help with development.

.. code:: python

    from flask.helpers import get_debug_flag
    if get_debug_flag():
        app.run()
    else:
        .... wsgi server run forever


Mixing Persistent Jobstores with Tasks from Config
######################################################

When using a persistent jobstore, do not register jobs from a configuration file. They should be registered by decorators (`see example <https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/decorated.py>`_), or by using the `add_job` method.


Mixing Persistent Jobstores with Tasks in __init__.py
######################################################

Tasks registered via decorator or the `add_job` method should not be loaded in your `app/__init__.py` if you are using a persistent job store. If they must be loaded upon app creation, a workaround would be as follows:

.. code:: python

    # app/__init__.py

    scheduler = APScheduler()
    db = SQLAlchemy()

    <other stuff>

    def create_app(config_class=Config):
        app = Flask(__name__)
        app.config.from_object(config_class)
        db.init_app(app)
        scheduler.init_app(app)
        scheduler.start()
        <other stuff>
        @app.before_first_request
        def load_tasks():
            from app import tasks

        return app


    # app/tasks.py

    @scheduler.task('cron', id='do_renewals', hour=9, minute=5)
    def scheduled_function():
        # your scheduled task code here


Your task will then be registered the first time that someone makes any request to the Flask app.

Trying to Load Tasks Outside Module-Level Import
################################################

If your task was loading correctly with the default memory jobstore, but does not load correctly from a persistent jobstore, this is because functions to be loaded as jobs must be available as module-level imports when used with persistent jobstores. They cannot be nested within other functions or classes.

So this function could be added using the `add_job` method:

.. code:: python

    # app/tasks.py

    def your_function():
        # your scheduled task code here

    # other_module.py

    scheduler.add_job(<details here>)

You could accomplish the same by importing modules that contain decorated functions (un-nested, at the module level):

.. code:: python

    # app/tasks.py

    @scheduler.task('cron', id='do_renewals', hour=9, minute=5)
    def scheduled_function():
        # your scheduled task code here


    # other_module.py

    from app import tasks


But this would not work:

.. code:: python

    # some_module.py

    def do_stuff():
      # do some stuff before registering a task
      # then attempt to register a task, which will fail due to nesting
      @scheduler.task('cron', id='do_renewals', hour=9, minute=5)
      def scheduled_function():
        # your scheduled task code here
