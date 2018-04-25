""" app/book/__init__py"""
from flask import Blueprint

book = Blueprint('book', __name__)

from . import views
