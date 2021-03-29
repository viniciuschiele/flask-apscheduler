"""Initialize any app extensions."""

from flask_apscheduler import APScheduler

scheduler = APScheduler()

# ... any other stuff.. db, caching, sessions, etc.
