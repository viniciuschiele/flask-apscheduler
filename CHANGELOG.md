# Changelog

### Version 1.4.0
 - Upgrade APScheduler to the version 3.2.0
 - Add new method to remove all jobs. Thanks [JWhy](https://github.com/JWhy).

### Version 1.3.7
 - Updated jobs were not being rescheduled (Issue #14)

### Version 1.3.6
 - Allows updating the trigger over the REST API (Issue #14)

### Version 1.3.5
 - Bug fix #9

### Version 1.3.4
 - Set a custom JSONEncoder to serialize date and datetime classes.

### Version 1.3.3
 - Improve json parsing

### Version 1.3.2
 - Bug fix

### Version 1.3.1
 - Make compatible with python 2.7

### Version 1.3.0
 - Change APIs Pause, Resume and Run to execute only with HTTP POST
 - Bug fix

### Version 1.2.1
 - Improve serialization and deserialization of triggers

### Version 1.2.0
 - Add REST API to add a new job
 - Add REST API to delete a job
 - Add REST API to update a job
 - Add REST API to pause a job
 - Add REST API to resume a job

### Version 1.1.0
 - Add new configuration attribute called SCHEDULER_VIEWS_ENABLED, default is False.
   From this version, the views are not loaded anymore by default.
 - Add more parameters to the job definition.
