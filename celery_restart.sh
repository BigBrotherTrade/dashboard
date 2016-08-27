#!/bin/bash
kill `cat celeryworker.pid`
kill `cat celerybeat.pid`
rm -f celery*.log
sleep 1
celery worker --pidfile=celeryworker.pid --logfile=celeryworker.log -A dashboard -l INFO --detach
celery beat --detach --pidfile=celerybeat.pid --logfile=celerybeat.log -A dashboard -l INFO
