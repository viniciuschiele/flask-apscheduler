# Changelog

### Version 1.10.1
 - Add LICENSE file to the package.

### Version 1.10.0
 - Add SCHEDULER_ENDPOINT_PREFIX setting to control the endpoint name. Thanks [andreicalistru](https://github.com/andreicalistru).
 - Set SCHEDULER_API_PREFIX default value to '/scheduler'. Thanks [andreicalistru](https://github.com/andreicalistru).

### Version 1.9.0
 - Add SCHEDULER_API_PREFIX to control the endpoint url. Thanks [FrEaKmAn](https://github.com/FrEaKmAn).
 - Fix issue #75

### Version 1.8.0
 - Add property to get the state of the scheduler.
 - Deprecate delete_job/delete_all_jobs in favor of remove_job/remove_all_jobs

### Version 1.7.1
 - Add possibility to resume the scheduler in paused state.

### Version 1.7.0
 - Add methods to pause and resume scheduler.

### Version 1.6.0
 - Add support for authentication to the API.
 - Add support for event listeners to the scheduler.

### Version 1.5.0
 - Set a min version for all the dependencies (Issue #18)

### Version 1.4.0
 - Upgrade APScheduler to the version 3.2.0
 - Add new method to remove all jobs. Thanks [JWhy](https://github.com/JWhy).

### Version 1.3.7
 - Updated jobs were not being rescheduled (Issue #14)

### Version 1.3.6
 - Allow updating the trigger over the REST API (Issue #14)

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
