#!/bin/bash
kill `cat celeryworker.pid`
kill `cat celerybeat.pid`
sleep 2
rm -f celery*.log
celery worker --pidfile=celeryworker.pid --logfile=celeryworker.log -A dashboard -l INFO --detach
celery beat --pidfile=celerybeat.pid --logfile=celerybeat.log -A dashboard -l INFO --detach
echo 'done!'
