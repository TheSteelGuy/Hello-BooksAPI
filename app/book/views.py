# app/book/views.py

import re
from flask import make_response, request, jsonify, Blueprint
from flask.views import MethodView
from datetime import datetime
# local imports
from app.models import User, Book
from app.authenticate import token_required

book_blueprint = Blueprint('book', __name__)


class BookView(MethodView):
    @classmethod
    @token_required
    def post(self, user_id):
        '''endpoint allows admin to add a new book information'''
        author = request.json.get('author')
        title = request.json.get('title')
        publisher = request.json.get('publisher')
        edition = request.json.get('edition')
        category = request.json.get('category')
        copies = request.json.get('copies')
        if title is None:
            return make_response(
                jsonify('provide book title in correct format')), 400
        if publisher is None:
            return make_response(
                jsonify('provide book publisher information in correct format')), 400
        if edition is None:
            return make_response(
                jsonify('provide book edition information in correct format')), 400
        if category is None:
            return make_response(
                jsonify('provide book category information in correct format')), 400
        if author.isdigit() or title.isdigit() or publisher.isdigit() or category.isdigit():
            return make_response(jsonify(
                {'message': 'book details must be alphabet'}
            )), 409
        if not re.findall(r'(^[A-Za-z]+\s[A-Za-z]+$)', author):
            return make_response(jsonify(
                {'message': 'author must be in form of Evalyn James'}
            )), 409
        if not isinstance(copies, int):
            return make_response(jsonify(
                {'message': 'copies must be provided in digits only'}
            )), 400
        if not User.admin_flag(user_id):
            return make_response(jsonify(
                {'message': 'you are not authorized to perform this action'}
            )), 401
        else:
            book = Book(
                author=author,
                book_title=title,
                publisher=publisher,
                edition=edition,
                category=category,
                copies=copies,
                user_id=user_id)
            if book.book_exist(author, title, edition):
                return make_response(jsonify(
                    {'message': 'book already exist, perhaps you can change its quantity.'}
                )), 409
            book.save_book()
            response = {
                'book_id': book.id,
                'book_title': book.book_title,
                'publisher': book.publisher,
                'edition': book.edition,
                'category': book.category,
                'copies': book.copies,
                'creator': book.creator_id
            }
            return make_response(jsonify(response)), 201

    @classmethod
    @token_required
    def put(self, book_id, user_id):
        '''modifys book information'''
        book_ = Book.query.filter_by(id=book_id).first()
        author = request.json.get('new_author')
        title = request.json.get('new_title')
        publisher = request.json.get('new_publisher')
        edition = request.json.get('new_edition')
        category = request.json.get('new_category')
        copies = request.json.get('new_copies')
        if book_:
            if title is None:
                return make_response(
                    jsonify('provide book title in correct format')), 400
            if publisher is None:
                return make_response(
                    jsonify('provide book publisher information in correct format')), 400
            if edition is None:
                return make_response(
                    jsonify('provide book edition information in correct format')), 400
            if category is None:
                return make_response(
                    jsonify('provide book category information in correct format')), 400
            if author.isdigit() or title.isdigit() or publisher.isdigit() or category.isdigit():
                return make_response(jsonify(
                    {'message': 'book details must be alphabet'}
                )), 409
            if not re.findall(r'(^[A-Za-z]+\s[A-Za-z]+$)', author):
                return make_response(jsonify(
                    {'message': 'author must be in form of Evalyn James'}
                )), 409
            if not isinstance(copies, int):
                return make_response(jsonify(
                    {'message': 'copies must be provided in digits only'}
                )), 409
            else:
                book_.author = author.strip()
                book_.book_title = title.strip()
                book_.publisher = publisher.strip()
                book_.edition = edition.strip()
                book_.category = category.strip()
                book_.copies = copies
                book_.updated_on = datetime.now()
                book_.save_book()
                return make_response(jsonify(
                    {'message': 'book details updated succesfully'}
                )), 201

        return make_response(jsonify(
            {'message': 'the book does not exist, you can instead add it'}
        )), 404

    @classmethod
    @token_required
    def delete(self, user_id, book_id):
        '''allows the admin to delete/remove book details'''
        book_ = Book.query.filter_by(id=book_id).first()
        user = User.query.filter_by(id=user_id).first()
        if book_:
            book_.delete_book()
            return make_response(jsonify({'message': 'you have deleted: {} by {}'.format(
                book_.book_title, book_.author), 'deleted by': user.name})), 200
        return make_response(jsonify(
            {'message': 'book does not exist'}
        )), 404

    def get(self, book_id=None):
        '''retrieves books and paginate them'''
        if book_id is None:
            try:
                limit = int(request.args.get('limit', default=3, type=int))
                page = int(request.args.get('page', default=1, type=int))
            except TypeError:
                return make_response(jsonify(
                    {'message': 'please ensure page and limit of books to be displayed are integers eg 5'}
                )), 400
            books = Book.query.paginate(page, limit, False)
            next_page = ''
            prev_page = ''
            pages = books.pages
            if books.has_prev:
                prev_page = '/books/?limit={}&page={}'.format(
                    limit, books.prev_num)
            if books.has_next:
                next_page = '/books/?limit={}&page={}'.format(
                    limit, books.next_num)
            books_catalog = [book.book_serialize() for book in books.items]
            if not books_catalog:
                return make_response(jsonify(
                    {'message': 'no books available'}
                )), 200
            return make_response(jsonify(
                books_catalog=books_catalog,
                prev_page=prev_page,
                next_page=next_page,
                pages=pages
            )), 200
        book_ = Book.query.filter_by(id=int(book_id)).first()
        return make_response(jsonify(book_.book_serialize()))


book_blueprint.add_url_rule(
    '/api/v1/books',
    view_func=BookView.as_view('books'),
    methods=[
        'POST',
        'GET'])
        
book_blueprint.add_url_rule(
    '/api/v1/books/<int:book_id>',
    view_func=BookView.as_view('book'),
    methods=['GET'])

book_blueprint.add_url_rule(
    '/api/v1/books/<int:book_id>',
    view_func=BookView.as_view('book_manipulate'),
    methods=[
        'PUT',
        'DELETE'])
