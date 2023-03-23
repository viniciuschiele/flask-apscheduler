***
API
***

Flask-APScheduler comes with a build-in API. This can be enabled/disabled in your flask configuration.

.. code-block:: python

    SCHEDULER_API_ENABLED: True


- /scheduler [GET] > returns basic information about the webapp
- /scheduler/pause [POST] > pauses job processing in the scheduler
- /scheduler/resume [POST] > resumes job processing in the scheduler
- /scheduler/start [POST] > starts the scheduler
- /scheduler/shutdown [POST] > shuts down the scheduler with `wait=True`
- /scheduler/shutdown [POST] + `json={'wait':False}` post data > shuts down the scheduler with `wait=False`
- /scheduler/jobs [POST json job data] > adds a job to the scheduler
- /scheduler/jobs/<job_id> [GET] > returns json of job details
- /scheduler/jobs [GET] > returns json with details of all jobs
- /scheduler/jobs/<job_id> [DELETE] > deletes job from scheduler
- /scheduler/jobs/<job_id> [PATCH json job data] > updates an already existing job
- /scheduler/jobs/<job_id>/pause [POST] > pauses a job, returns json of job details
- /scheduler/jobs/<job_id>/resume [POST] > resumes a job, returns json of job details
- /scheduler/jobs/<job_id>/run [POST] > runs a job now, returns json of job details


Scheduler
---------

Other commands can be passed to the scheduler and are rather self explanatory:

- scheduler.start()
- scheduler.shutdown()
- scheduler.pause() > stops any job from starting. Already running jobs not affected.
- scheduler.resume() > allows scheduled jobs to begin running.
- scheduler.add_listener(<callback function>,<event>)
- scheduler.remove_listener(<callback function>)
- scheduler.add_job(<id>,<function>, \*\*kwargs)
- scheduler.remove_job(<id>, \*\*<jobstore>)
- scheduler.remove_all_jobs(\*\*<jobstore>)
- scheduler.get_job(<id>,\*\*<jobstore>)
- scheduler.modify_job(<id>,\*\*<jobstore>, \*\*kwargs)
- scheduler.pause_job(<id>, \*\*<jobstore>)
- scheduler.resume_job(<id>, \*\*<jobstore>)
- scheduler.run_job(<id>, \*\*<jobstore>)
- scheduler.authenticate(<function>)