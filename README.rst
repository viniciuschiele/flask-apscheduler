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

Documentation
===============
Take a look at the examples_ to see how it works.

Installation
===============
You can install Flask-APScheduler via Python Package Index (PyPI_),::

    $ pip install Flask-APScheduler

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

