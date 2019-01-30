<h1>Common Issues</h1>

<h3>Context Issues</h3>

On each function registered to the scheduler that requires Flask app context, assuming your `APScheduler` object is called `scheduler`, include:

```python
with scheduler.app.app_context():
  # your code
```

<h3>Mixing Persistent Jobstores with Tasks from Config</h3>

When using a persistent jobstore, do not register jobs from a configuration file. They should be registered by decorators [(example)](https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/decorated.py) or by using the `add_job` method.

<h3>Mixing Persistent Jobstores with Tasks in __init__.py</h3>

Tasks registered via decorator or the `add_job` method should not be loaded in your `app/__init__.py` if you are using a persistent job store. If they must be loaded upon app creation, a workaround would be as follows:

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

@scheduler.task('cron', id='do_renewals', hour=9, minute=5)
def scheduled_function():
    # your scheduled task code here
```

Your task will then be registered the first time that someone makes any request to the Flask app.

<h3>Trying to Load Tasks Outside Module-Level Import</h3>

If your task was loading correctly with the default memory jobstore, but does not load correctly from a persistent jobstore, this is because functions to be loaded as jobs must be available as module-level imports when used with persistent jobstores. They cannot be nested within other functions or classes.

So this function could be added using the `add_job` method:
```python
# app/tasks.py

def your_function():
    # your scheduled task code here
```
```
```python
# other_module.py

scheduler.add_job(<details here>)
```

You could accomplish the same by importing modules that contain decorated functions:
```python
# app/tasks.py

@scheduler.task('cron', id='do_renewals', hour=9, minute=5)
def scheduled_function():
    # your scheduled task code here
```
```
```python
# other_module.py

from app import tasks
```

But this would not work:
```python
# some_module.py

def do_stuff():
  # do some stuff before registering a task
  # then attempt to register a task, which will fail due to nesting
  @scheduler.task('cron', id='do_renewals', hour=9, minute=5)
  def scheduled_function():
    # your scheduled task code here
