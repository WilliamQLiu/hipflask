#!/usr/bin/env bash
echo "Running celery worker script!";
sleep 30  # wait for other servers to start up
#pip install -r /web/requirements.txt
#celery -A hipflask.celery worker  # start up celery worker
tail -f /dev/null  # keep container up