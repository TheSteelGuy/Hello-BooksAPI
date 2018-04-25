"""
   app/authenticate.py
   coding:utf-8
"""
# third party imports
from functools import wraps
from flask import request, jsonify, make_response
# local imports
from app.models import User


def token_required(func):
    """ modifyies the authenication token function in the database models."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        """ function chcks token"""
        auth_header = request.headers.get('Authorization')
        if auth_header is None:
            return make_response(jsonify(
                {'message': 'provide a token in the authorization header, please'}
            )), 403
        auth_token = auth_header.split("Bearer ")[1]
        if auth_token:
            user_id = User.decode_token(auth_token)
            if not isinstance(user_id, str):
                user_id = user_id
            else:
                response = {
                    'message': user_id
                }
                return make_response(jsonify(response)), 401
        else:
            response = {
                'message': 'invalid token detected'
            }
            return make_response(jsonify(response)), 401
        return func(user_id=user_id, *args, **kwargs)
    return wrapper
