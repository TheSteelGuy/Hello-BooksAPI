""" app/config.py
    coding:utf-8
"""

import os


class Baseconfig:
    """base config"""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DBASE_URI')


class Productionconfig(Baseconfig):
    """production based config"""
    TESTING = False


class Developmentconfig(Baseconfig):
    """config for development"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/hello_db"
    #SQLALCHEMY_DATABASE_URI = 'mysql://root:collo0@localhost/lib_app'
    SECRET_KEY = os.urandom(10)


class Testconfig(Baseconfig):
    """For testing the application"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:postgres@localhost/test_libapp"
    #SQLALCHEMY_DATABASE_URI = "mysql://root:collo0@localhost/test_catalog"
    SECRET_KEY = os.urandom(10)


app_config = {
    'development': Developmentconfig,
    'testing': Testconfig,
    'production': Productionconfig

}
