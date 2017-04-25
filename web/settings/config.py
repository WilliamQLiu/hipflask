import os


class BaseConfig(object):
    """ Base configuration """
    SECRET_KEY = os.environ['SECRET_KEY']
    DEBUG = os.environ['DEBUG']  # True
    DB_NAME = os.environ['DB_NAME']  # e.g. postgres
    DB_USER = os.environ['DB_USER']  # e.g. postgres
    DB_PASS = os.environ['DB_PASS']  # e.g. postgres
    DB_SERVICE = os.environ['DB_SERVICE']  # e.g. postgres
    DB_PORT = os.environ['DB_PORT']  # e.g. 5432
    SQLALCHEMY_DATABASE_URI = 'postgresql://{0}:{1}@{2}:{3}/{4}'.format(
        DB_USER, DB_PASS, DB_SERVICE, DB_PORT, DB_NAME
    )


class DevConfig(BaseConfig):
    """ Development Configuration """
    DEBUG = True


class ProdConfig(BaseConfig):
    """ Production Configuration """
    DEBUG = False