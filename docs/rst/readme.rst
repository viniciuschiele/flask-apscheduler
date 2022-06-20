=================================
Flask-APScheduler
=================================
Flask-APScheduler is a Flask extension which adds support for the APScheduler.

|Version| |Tests| |Coverage| |Docs|

Features
===============
- Loads scheduler configuration from Flask configuration.
- Loads job definitions from Flask configuration.
- Allows to specify the hostname which the scheduler will run on.
- Provides a REST API to manage the scheduled jobs.
- Provides authentication for the REST API.
- Integrates with `Flask Blueprints <https://github.com/viniciuschiele/flask-apscheduler/tree/master/examples/application_factory>`_

Installation
===============
You can install Flask-APScheduler via Python Package Index (PyPI_)

.. code:: python

    pip install Flask-APScheduler

Documentation
===============

`See Flask APSchedulers Documentation. <https://viniciuschiele.github.io/flask-apscheduler/>`_

Feedback
===============
Please use the Issues_ for feature requests and troubleshooting usage.

.. |Version| image:: https://img.shields.io/pypi/v/flask-apscheduler.svg
    :target: https://pypi.python.org/pypi/Flask-APScheduler

.. |Tests| image:: https://github.com/viniciuschiele/flask-apscheduler/actions/workflows/tests.yml/badge.svg
    :target: https://github.com/viniciuschiele/flask-apscheduler/actions/workflows/tests.yml

.. |Coverage| image:: https://codecov.io/github/viniciuschiele/flask-apscheduler/coverage.svg
    :target: https://codecov.io/github/viniciuschiele/flask-apscheduler

.. |Docs| image:: https://github.com/viniciuschiele/flask-apscheduler/actions/workflows/docs.yml/badge.svg
    :target: https://github.com/viniciuschiele/flask-apscheduler/actions/workflows/docs.yml

.. _examples: https://github.com/viniciuschiele/flask-apscheduler/tree/master/examples

.. _PyPi: https://pypi.python.org/pypi/Flask-APScheduler

.. _Issues: https://github.com/viniciuschiele/flask-apscheduler/issues
