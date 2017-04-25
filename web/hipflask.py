from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask import request, render_template

from settings.config import BaseConfig

application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)


@application.route("/")
def hello_world():
    return "Hey there!"


@application.route("/<name>")
def hello_name(name):
    return "Hello {}!".format(name)


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0")
