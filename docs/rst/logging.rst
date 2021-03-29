*******
Logging
*******


Logging
-------

All scheduler events can be used to trigger logging functions. See `APScheduler <https://apscheduler.readthedocs.io/en/stable/userguide.html#scheduler-events>`_ for a list of available events.

If you are using your Flask app context inside of a function triggered by a scheduler event can include something like this

.. code-block:: python

    def blah():
        with scheduler.app.app_context():
            # do stuff

    scheduler.add_listener(blah, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)




