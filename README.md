# hipflask

hipflask is a web app for me to try out [Docker](https://www.docker.com), [Docker Compose](https://docs.docker.com/compose/), and the Python micro web-framework [Flask](http://flask.pocoo.org/docs/0.12/).

## Overview

The tech stack currently uses:

* nginx as a reverse proxy
* postgresql as a relational database
* flask as the web server
* redis as an in-memory database and message-broker 
* celery as a distributed task queue (not yet working for Docker)

## Getting started

### Flask

If you only want to use flask locally, here is how to get started:

    $pip install -r requirements  # to install libraries, I recommend a virtualenv
    $export FLASK_APP = hipflask.py  # set environment variable to our app
    $flask run --no-reload   # run flask locally
    $python -m unittest discover .  # run unit tests inside hipflask dir
    
#### Flask Usage

After running, you should be able to see the server locally: http://127.0.0.1:5000

To see an example template, view: http://127.0.0.1:5000/companies/

###Docker and Docker Compose

Make sure docker and docker-compose is installed. Go to the directory where 'docker-compose.yml' is and then run:

    $docker-compose up  # might take a while to build the first time
    $docker-compose run --rm web python /web/hipflask/create_db.py  # To add some data into the db
    $docker-compose down  # when you want to shut down the containers

### TO-DOs

In the future I want to:

* Fix Celery Workers
* Create integration test examples
* Organize directories
* Setup continuous integration with GitHub and CircleCI
* Setup continuous deployment on AWS
* Setup monitoring

### License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
