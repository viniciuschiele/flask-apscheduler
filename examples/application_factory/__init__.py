"""Flask APScheduler example using Flask's Application Factory setup.

Run using:

.. code ::python

    pip install flask-apscheduler
    export FLASK_ENV=development && export FLASK_DEBUG=1 && export FLASK_APP=__init__ && flask run

"""

import logging
import os

from flask import Flask

from .extensions import scheduler
from .settings import DevelopmentConfig


def create_app():
    """Create a new app instance."""

    def is_debug_mode():
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    # pylint: disable=W0621
    app = Flask(__name__)

    app.config.from_object(DevelopmentConfig)
    scheduler.init_app(app)

    logging.getLogger("apscheduler").setLevel(logging.INFO)

    # pylint: disable=C0415, W0611
    with app.app_context():
        # pylint: disable=W0611
        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            from . import tasks  # noqa: F401

            scheduler.start()

        from . import events, web  # noqa: F401

        app.register_blueprint(web.web_bp)

        return app


app = create_app()

if __name__ == "__main__":
    app.run()
