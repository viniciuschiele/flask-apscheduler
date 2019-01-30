<h1>Common Issues</h1>

<h3>Context Issues</h3>

On each function registered to the scheduler that requires Flask app contect, assuming your `APScheduler` object is called `scheduler`, include:

```python
with scheduler.app.app_context():
  # your code
```

<h3>Other Issues</h3>

1. When using a persistent jobstore, do not register jobs from a configuration file. They should be registered by decorators [(example)](https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/decorated.py) or by using the `add_job` method.

2. Tasks registered via decorator or the `add_job` method should not be loaded in your `app/__init__.py` if you are using a persistent job store. If they must be loaded upon app creation, a workaround would be as follows:

```python
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
```
```python
# app/tasks.py

@scheduler.task(
    'cron',
    id='do_renewals',
    hour=9,
    minute=5,
    misfire_grace_time=10800,
)
def your_function():
    # your scheduled task code here
```

Your task will then be registered the first time that someone makes any request to the Flask app.
