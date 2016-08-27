#!/bin/bash
kill `cat celeryworker.pid`
sleep 2
rm -f celery*.log
celery worker --pidfile=celeryworker.pid --logfile=celeryworker.log -A dashboard -l INFO --detach -B
echo 'done!'
