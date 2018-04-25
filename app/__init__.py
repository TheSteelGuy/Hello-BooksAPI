"""
app/__init__.py
coding:utf-8

the init file controls the application
all essential configaration are done here
"""
# third party imports
from flask_api import FlaskAPI
from flask_cors import CORS
# local imports
from app.config import app_config
from . error import method_not_allowed, server_error, resource_not_found
from .models import db


def create_app(config_name):
    ''' functions which creates the app'''
    app = FlaskAPI(__name__)
    CORS(app)
    app.url_map.strict_slashes = False
    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    # import and register blueprints
    from .book.views import book_blueprint
    from .user.views import user_blueprint
    from app.auth import auth as auth_blueprint
    app.register_blueprint(book_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)
    app.register_error_handler(500, server_error)
    app.register_error_handler(405, method_not_allowed)
    app.register_error_handler(404, resource_not_found)

    return app
