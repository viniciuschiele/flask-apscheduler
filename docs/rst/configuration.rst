*************
Configuration
*************


Configuration options specific to ``Flask-APScheduler``:

.. code-block:: python

    SCHEDULER_API_ENABLED: bool (default: False)
    SCHEDULER_API_PREFIX: str (default: "/scheduler")
    SCHEDULER_ENDPOINT_PREFIX: str (default: "scheduler.")
    SCHEDULER_ALLOWED_HOSTS: list (default: ["*"])

Configuration options specific to ``APScheduler``:

.. code-block:: python

    SCHEDULER_JOBSTORES: dict
    SCHEDULER_EXECUTORS: dict
    SCHEDULER_JOB_DEFAULTS: dict
    SCHEDULER_TIMEZONE: dict

For more details, check out `APScheduler <https://apscheduler.readthedocs.io/en/stable/userguide.html#configuring-the-scheduler>`_
