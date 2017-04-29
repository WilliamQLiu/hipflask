"""
A sample Flask app
Usually models, apis, routes, are split to different dirs.

To run locally (without Docker):
$export FLASK_APP = hipflask.py
$flask run --no-reload
"""
from __future__ import absolute_import
import os
from datetime import datetime

from flask import (
    Flask, request, Response, render_template, jsonify, redirect, flash, url_for,
    make_response
)
from flask_restful import Resource, Api, reqparse
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from redis import Redis
from celery import Celery
import pandas
import numpy


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
    UPLOAD_FOLDER = "/uploads/"
    ALLOWED_EXTENSIONS = set(["csv"])

# Initial Setup
application = Flask(__name__)
application.config.from_object(BaseConfig)
db = SQLAlchemy(application)  # for database connection
api = Api(application)  # for restful api


# Redis Setup
redis = Redis(host='0.0.0.0', port=6379)  # a redis instance is thread safe, can use on global level
application.config.update(
    CELERY_BROKER_URL='redis://0.0.0.0:6379',
    CELERY_RESULT_BACKEND='redis://0.0.0.0:6379'
)

# Celery Setup
def make_celery(app):
    celery = Celery(app.import_name, backend=app.config["CELERY_RESULT_BACKEND"],
                    broker=app.config["CELERY_BROKER_URL"])
    celery.conf.update(app.config)
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)
    celery.Task = ContextTask
    return celery

celery = make_celery(application)

@celery.task()
def add_together(a, b):
    """ Some long task """
    return a + b


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
        :param urltext: (type str) checks if url contains this text (default None)
        :param limit: (type int) is items returned (default None, returns all) 
        :return list of JSON buzz items
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


api.add_resource(BuzzItem, "/buzz/<int:id>/")
api.add_resource(BuzzList, "/buzz/")

# Routes
@application.route("/")
def hello_world():
    return render_template("index.html")


@application.route("/buzz/simple/", methods=["GET", "POST"])
def buzz_norest():
    if request.method == "POST":
        redis.incr("counter")
        counter = redis.get("counter")
        return jsonify({"counter": counter})
    buzzing = Buzz.query.limit(3)
    return render_template('buzz.html', buzzing=buzzing)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False


def transform_companies_data(request, data):
    """
    :param request: the request
    :param data: dict containing error, message, and dfs
    :return: data: dict containing error, message, and merged dataframe
    """
    try:
        # get dataframes of uploaded files
        df_companies = data["dfs"]["companies"]
        df_daily = data["dfs"]["daily"]

        # merge and change data types; can do additional data validation here
        df_merged = df_daily.merge(df_companies, on="id", how="inner")
        df_merged["date"] = pandas.to_datetime(df_merged["date"])
        df_merged["value"] = df_merged["value"].astype(int)

        # filter for start_date and end_dates
        start_date = request.form.get("start_date")
        if start_date == "":
            start_date = None
        else:
            start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = request.form.get("end_date")
        if end_date == "":
            end_date = None
        else:
            end_date = datetime.strptime(end_date, "%Y-%m-%d")
        if(start_date and end_date):
            pass
        elif(start_date):
            end_date = df_merged.date.max()
        elif(end_date):
            start_date = df_merged.date.min()
        else:
            start_date = df_merged.date.min()
            end_date = df_merged.date.max()
        # Should check more data validation (e.g. start_date > end_date)
        date_range_index = pandas.date_range(start_date, end_date)

        # multilevel index by date with forward fill for missing values
        df_grouped = df_merged.groupby(["date", "id"]).sum()
        (date_index, id_index) = df_grouped.index.levels
        new_index = pandas.MultiIndex.from_product([date_range_index, id_index])
        new_df = df_grouped.reindex(new_index)
        new_df = new_df.reset_index()
        new_df.columns = ["date", "id", "value"]

        # Get difference (last n rows) based on grouping by company "id"
        n_difference = request.form.get("n")
        if(is_number(n_difference)):
            pass
        else:
            n_difference = 1
        diff = lambda x: x["value"].replace(0, numpy.NaN).dropna().diff(n_difference)
        df_grouped = new_df.groupby("id")
        new_df["difference"] = df_grouped.apply(diff).reset_index(0, drop=True)
    except Exception as e:
        data["error"] = True
        data["message"] = str(e)
        data["dfs"]["merged"] = None
        return data

    data["error"] = False
    data["message"] = "Successfully merged files"
    data["dfs"]["merged"] = new_df
    return data


def validate_companies_file_upload(request):
    """
    Validate file uploads 
    :param request: the request
    :return data: dict that contains the following keys
        error: boolean (default False)
        message: string of error or success message (default None)
        dfs: dict with keys holding dataframes
    """
    data = {
        "error": False, "message": None,
        "dfs": {"daily": None, "companies": None}
    }

    # check if files are there and correct file type
    companies = request.files.get("companies", None)
    daily = request.files.get("daily", None)
    if not(companies and daily):
        data["error"] = True
        data["message"]= "Missing file(s): must be named 'companies.csv' and 'daily.csv'"
    elif (companies.content_type != "text/csv" or daily.content_type != "text/csv"):
        data["error"] = True
        data["message"] = "File type mismatch: check that file types "
    else:
        data["dfs"]["daily"] = pandas.read_csv(daily)
        data["dfs"]["companies"] = pandas.read_csv(companies)
    return data


@application.route("/companies/", methods=["GET", "POST"])
def transform_daily_company_files():
    """
    Merge two files (daily.csv, companies.csv) based on id, 
    then return new cleaned data file (export.csv)
    """
    if request.method == "POST":
        result = validate_companies_file_upload(request)
        if(result["error"]):
            flash(result["message"])
            return redirect(url_for("transform_daily_company_files"))

        result = transform_companies_data(request, result)
        if(result["error"]):
            flash(result["message"])
            return redirect(url_for("transform_daily_company_files"))

        # send csv file if data was merged successfully
        csv_file = result["dfs"]["merged"].to_csv(index=False)
        response = make_response(csv_file)
        response.headers["Content-Disposition"] = "attachment; filename=export.csv"
        response.headers["Content-Type"] = "text/csv"
        response.status = "200 OK"
        response.status_code = 200
        return response
    return render_template("transform.html")


if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0")
