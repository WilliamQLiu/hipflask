#!/usr/bin/env bash

echo "Running uwsgi script!";
sleep 5  # wait for server to start up
/usr/local/bin/uwsgi --ini /web/settings/uwsgi.ini  # start uwsgi

