"""app/admin/views.py"""

from flask import make_response, request, jsonify
from werkzeug.security import generate_password_hash
# local imports
from app.models import User
from app.models import TokenBlacklisting
from app.authenticate import token_required
from . import auth


@auth.route('/auth/api/v1/register', methods=['POST'])
def register():
    """method to handle register requests"""
    if request.method == 'POST':
        details = request.get_json()
        name = details.get('name')
        email = details.get('email')
        national_id = details.get('national_id')
        is_admin = details.get('admin')
        password = details.get('password')
        confirm_pwd = details.get('confirm_pwd')
        if len(name) < 4:
            return make_response(jsonify(
                {'message': 'name must be four letters or more!'}
            )), 409
        if not User.validate_email(email):
            return make_response(jsonify(
                {'message': "Invalid email"}
            )), 409
        if password != confirm_pwd:
            return make_response(jsonify(
                {'message': 'password mistmatch'}
            )), 400
        if len(password) < 4:
            return make_response(jsonify(
                {'message': 'password too short'}
            )), 409
        if str(national_id).isalpha():
            return make_response(jsonify(
                {'message': 'national id must be digits'}
            )), 400
        if name.isdigit():
            return make_response(jsonify(
                {'message': 'Name must be an alphabet'}
            )), 400
        user = User.query.filter_by(email=email).first()
        if user:
            return make_response(jsonify(
                {'message': 'user already registred, login'}
            )), 200
        user = User(
            name=name,
            email=email,
            national_id=national_id,
            password=password,
            is_admin=is_admin)
        user.save_user()
        auth_token = user.token_generate(user.id)
        return make_response(jsonify(
            {
                'message': 'registration successfull',
                'token': auth_token.decode()
            }
        )), 201
    return None


@auth.route('/auth/api/v1/login', methods=['POST'])
def login():
    """handles login requests"""
    if request.method == 'POST':
        details = request.get_json()
        email = details.get('email')
        password = details.get('password')
        user = User.query.filter_by(email=email).first()
        if not user:
            return make_response(jsonify(
                {'message': 'user does not exist'}
            )), 404
        if user and user.verify_password(password):
            auth_token = user.token_generate(user.id)
            return make_response(jsonify(
                {
                    'message': 'successfully logged in',
                    'token': auth_token.decode()
                }
            )), 200
        return make_response(jsonify(
            {'message': 'invalid credentials, check details and try again'}
        )), 401
    return None


@auth.route('/auth/api/v1/logout', methods=['POST'])
@token_required
def logout(user_id):
    """Logout a registered user."""
    if request.method == 'POST':
        auth_header = request.headers.get('Authorization')
        auth_token = auth_header.split("Bearer ")[1]
        if auth_token and not TokenBlacklisting.verify_token(
                auth_token=auth_token):
            auth_data = User.decode_token(auth_token)
            if not isinstance(auth_data, str):
                blacklist_token = TokenBlacklisting(token=auth_token)
                try:
                    blacklist_token.save_token()
                    user = User.query.filter_by(id=user_id).first()
                    return make_response(
                        jsonify({
                            'message': 'see you soon {}, you have successfully logged out'.format(user.name)
                        })), 200
                except Exception as e:
                    return make_response(jsonify({"message": e})), 400
            return make_response(jsonify({"message": auth_data})), 404
        return make_response(
            jsonify({
                "message": "Please provide a valid token"
            })), 403
    return None


@auth.route('/api/auth/reset-password', methods=['POST'])
def reset_password():
    """allowes user to reset password"""
    if request.method == 'POST':
        email = request.json.get('email')
        new_password = request.json.get('new_password')
        if len(new_password.strip()) < 4:
            return make_response(jsonify(
                {'message': 'password too short'}
            )), 409
        user = User.query.filter_by(email=email).first()
        if user:
            user.password_hash = generate_password_hash(new_password)
            user.save_user()
            return make_response(jsonify(
                {
                    'message': 'password reset successful',
                    'your new password': new_password
                }
            )), 201
        return make_response(jsonify(
            {'message': 'Wrong email, please provide a valid email and try again'}
        )), 401
    return None
