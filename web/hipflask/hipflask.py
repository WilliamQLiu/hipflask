from __future__ import absolute_import
import os
from datetime import datetime

from flask import Flask, request, render_template, jsonify
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from redis import Redis

class BaseConfig(object):
    """ Base configuration """
    SECRET_KEY = os.environ.get("SECRET_KEY", "5(15ds+i2+%ik6z&!yer+ga9m=e%jcqiz_5wszg)r-z!2--b2d")
    DEBUG = os.environ.get("DEBUG", True)
    DB_NAME = os.environ.get("DB_NAME", "postgres")
    DB_USER = os.environ.get("DB_USER", "postgres")
    DB_PASSWORD = os.environ.get("DB_PASS", "postgres")
    DB_SERVICE = os.environ.get("DB_SERVICE", "localhost")
    DB_PORT = os.environ.get("DB_PORT", 5432)
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASSWORD, DB_SERVICE, DB_PORT, DB_NAME
    )

# Initial Setup
application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)  # for database connection
db.drop_all()  # Drop all existing database tables
db.create_all()  # Create database and database tables
api = Api(application)  # for restful api
redis = Redis(
    host='0.0.0.0',
    port=6379
)  # a redis instance is thread safe, can use on global level


# Redis


# Models
class Buzz(db.Model):
    __tablename__ = "buzz"

    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    pub_date = db.Column(db.DateTime)

    def __init__(self, url, pub_date=None):
        self.url = url
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

    def __repr__(self):
        return "<Buzz %r>" % (self.id)

    def to_dict(self):
        """ Convert Python object to dictionary """
        return {"id": self.id, "url": self.url, "pub_date": self.pub_date}

    def to_json(self):
        """ Convert Buzz item from Python object to JSON """
        return jsonify(id=self.id, url=self.url, pub_date=self.pub_date)


# API Resources
class BuzzItem(Resource):
    """ Single Buzz item for GET, PUT, DELETE """

    def get(self, id):
        """ GET a single Buzz resource """
        obj = Buzz.query.get_or_404(id)
        return obj.to_json()

    def put(self, id):
        obj = Buzz.query.get_or_404(id)
        # TODO: Finish PUT example
        return "TODO: PUT"

    def delete(self, id):
        """ DELETE a single Buzz resource """
        # TODO: Finish Delete example
        return "TODO: DELETE"


class BuzzList(Resource):
    """ GET list of buzz items or POST to create new buzz item """

    def get(self):
        """
        GET list of buzz items
        :argument 'urltext' (type str) checks if url contains this text (default None)
        :argument 'limit' (type int) is items returned (default None, returns all) 
        :returns list of JSON buzz items
        """
        parser = reqparse.RequestParser()
        parser.add_argument("urltext", type=str, help="URL contains text")
        parser.add_argument("limit", type=int, help="Limit number of items returned")
        args = parser.parse_args()
        urltext = args.get("urltext", None)
        limit = args.get("limit", None)
        if urltext and limit:
            objs = Buzz.query.filter(Buzz.url.contains(urltext)).limit(limit)
        elif urltext:
            objs = Buzz.query.filter(Buzz.url.contains(urltext))
        elif limit:
            objs = Buzz.query.limit(limit).all()
        else:
            objs = Buzz.query.all()
        data = []
        for obj in objs:
            data.append(obj.to_dict())
        return jsonify(data)

    def post(self):
        """ Create a single Buzz resource """
        # TODO: Finish POST example
        return "TODO: POST"


api.add_resource(BuzzItem, '/buzz/<int:id>/')
api.add_resource(BuzzList, '/buzz/')


# Routes
@application.route("/")
def hello_world():
    return render_template('index.html')


@application.route("/buzz/simple/", methods=["GET", "POST"])
def buzz_norest():
    if request.method == "POST":
        redis.incr("counter")
        counter = redis.get("counter")
        return jsonify({"counter": counter})
    buzzing = Buzz.query.limit(3)
    return render_template('buzz.html', buzzing=buzzing)


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0")
