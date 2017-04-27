#!/bin/bash

echo "Running Post Script!";
/usr/local/bin/uwsgi --ini /web/settings/uwsgi.ini  # start uwsgi
