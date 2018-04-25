"""app/home/views.py"""

from datetime import date, timedelta
from flask import make_response, jsonify, Blueprint
from flask.views import MethodView
# local imports
from app.models import Book, User, Borrow
from app.authenticate import token_required


user_blueprint = Blueprint('user', __name__)

class Index(MethodView):
    """index/home url class"""
    @staticmethod
    def get():
        """get requests for homepage"""
        return make_response(jsonify(
            {
                'message': 'welcome to the hello-books API you can register in order to get the most out of the app'
            }
        )), 200


class UserViews(MethodView):
    """class handling user actions"""
    @classmethod
    @token_required
    def post(cls, book_id, user_id):
        ''' allows user to rent book'''
        book_borrowed = Borrow.query.filter_by(book_id=book_id).first()
        if book_borrowed is None:
            book = Book.query.filter_by(id=book_id).first()
            if not book:
                return make_response(jsonify(
                    {'message': 'book does not exist, check its ID and try again'}
                )), 404
            if book.copies <= 0:
                return make_response(jsonify(
                    {'message': 'book out of stock, try again later'}
                )), 404
            user = User.query.filter_by(id=user_id).first()
            borrow = Borrow(
                book_id=book.id,
                email=user.email,
                national_id=user.national_id,
                borrower_id=user_id
            )
            borrow.save_borrowed()
            book.copies -= 1
            book.save_book()
            return_date = date.today() + timedelta(days=30)
            return make_response(jsonify(
                {
                    'message': 'hi {}, you have borrowed {} by {}'.format(user.name, book.book_title, book.author), 
                    'note': 'return this book by, {}'.format(return_date.isoformat())
                } 
            )), 200
        return make_response(jsonify(
            {'message': 'you cant borrow this book as you have not returned it yet'}
        )), 409

    @classmethod
    @token_required
    def put(cls, book_id):
        """method allows user to return rented books"""
        book_to_return = Borrow.query.filter_by(book_id=book_id).first()
        if book_to_return:
            if book_to_return.return_status is True:
                return make_response(jsonify(
                    {'message': 'you have already returned this book'}
                )), 409
            book_to_return.return_status = True
            book_to_return.save_borrowed()
            book = Book.query.filter_by(id=book_id).first()
            book.copies += 1
            book.save_book()
            return make_response(jsonify(
                {'message': 'you have successfully returned;{}'.format(book.book_title)}
            )), 200
        return make_response(jsonify(
            {'message': 'Book specified does not exist, check for correct id and try again'}
        )), 404


user_blueprint.add_url_rule(
    '/', view_func=Index.as_view('index'), methods=['GET']
)

user_blueprint.add_url_rule(
    '/api/v1/users/books/<int:book_id>',
    view_func=UserViews.as_view('borrow-book'), methods=['POST', 'PUT']
)
