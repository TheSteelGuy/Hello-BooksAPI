"""
app/models.py
coding:utf-8
the model class contains the application models,
and how various entities are relating within the database such as,
relationship between user and books
"""
# third party imports
import re
from datetime import datetime, timedelta
import jwt
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import current_app


db = SQLAlchemy()


class User(db.Model):
    """ handles users of the app"""
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(60))
    email = db.Column(db.String(100), unique=True, nullable=False)
    national_id = db.Column(db.Integer, nullable=False)
    password_hash = db.Column(db.String(200))
    is_admin = db.Column(db.Boolean(), nullable=False)
    books = db.relationship(
        'Borrow',
        backref='users',
        lazy='dynamic',
        order_by='Borrow.id',
        cascade='all, delete-orphan'
    )

    def __init__(self,
                 name,
                 email,
                 national_id,
                 password,
                 is_admin=None):
        """constructor method which create the attributes of User() objects"""
        self.name = name
        self.email = email
        self.national_id = national_id
        self.password_hash = generate_password_hash(password)
        self.is_admin = False if is_admin is None else True

    @staticmethod
    def admin_flag(user_id):
        """identifies users as admins or normal users, enable admins to manage books"""
        user = User.query.filter_by(id=user_id).first()
        if user.is_admin:
            return True
        return False

    @property
    def password(self):
        """raises attribute error if access to password is tried"""
        return AttributeError('Password is not readable, attribute')

    def verify_password(self, password):
        """verify password against the  password hash"""
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def validate_email(email):
        """Ensure valid email"""
        return bool(
            re.findall(
                r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
                email))

    def token_generate(self, user_id):
        """method which generates token for users"""
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=200),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            encoded_token = jwt.encode(
                payload, current_app.config['SECRET_KEY'], algorithm='HS256'
            )
            return encoded_token

        except Exception:
            return str(Exception)

    @staticmethod
    def decode_token(token_auth):
        """decodes the token"""
        try:
            payload = jwt.decode(
                token_auth,
                current_app.config['SECRET_KEY'],
                algorithm='HS256')
            token_blacklisted = TokenBlacklisting.verify_token(token_auth)
            if token_blacklisted:
                return "Invalid token.Login"
            return payload['sub']
        except jwt.ExpiredSignatureError:
            return "Token Expired.Login"
        except jwt.InvalidTokenError:
            return "Invalid header padding"

    def save_user(self):
        """saves a user to the database"""
        db.session.add(self)
        db.session.commit()

    def __repr__(self):
        """string represntaion for the user class"""
        return '<user:{}>'.format(self.name)


class Book(db.Model):
    """class book handles book"""
    __tablename__ = 'books'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    author = db.Column(db.String(60), nullable=False)
    book_title = db.Column(db.String(60), nullable=False)
    publisher = db.Column(db.String(60), nullable=False)
    edition = db.Column(db.String(100), unique=False, nullable=False)
    category = db.Column(db.String(40), unique=False, nullable=False)
    copies = db.Column(db.Integer, nullable=False)
    creator_id = db.Column(db.Integer, db.ForeignKey(User.id))
    added_on = db.Column(db.DateTime, default=datetime.now)
    updated_on = db.Column(db.TIMESTAMP, server_onupdate=db.func.now())
    borrower = db.relationship(
        'Borrow',
        backref='books',
        lazy='dynamic',
        order_by='Borrow.book_id',
        cascade='all, delete-orphan'
    )

    def __init__(
            self,
            author,
            book_title,
            publisher,
            edition,
            category,
            copies,
            user_id):
        """ book constructor method which sets book attributes"""
        self.author = author
        self.book_title = book_title
        self.publisher = publisher
        self.edition = edition
        self.category = category
        self.copies = copies
        self.creator_id = user_id

    @staticmethod
    def book_exist(author, title, edition):
        """checks if a book exist"""
        book = Book.query.filter_by(
            author=author,
            book_title=title,
            edition=edition).first()
        if book:
            return True
        return False

    def change_copies(self, book_id):
        """ method for changing copies of books"""
        book = Book.query.filter_by(id=book_id).first()
        if book:
            self.copies += 1
            db.session.commit()

    def delete_book(self):
        """delete this book"""
        db.session.delete(self)
        db.session.commit()

    def book_serialize(self):
        """returns a book dictionary"""
        return {
            'book_id': self.id,
            'author': self.author,
            'publisher': self.publisher,
            'edition': self.edition,
            'category': self.category,
            'copies': self.copies
        }

    def save_book(self):
        """saves book to database"""
        db.session.add(self)
        db.session.commit()


class Borrow(db.Model):
    """handles users who have borrowed"""
    __tablename__ = 'borrowers'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False)
    national_id = db.Column(db.Integer, nullable=False)
    borrower_id = db.Column(db.Integer, db.ForeignKey(User.id))
    return_status = db.Column(db.Boolean())
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id))

    def __init__(self, book_id, email, national_id, borrower_id):
        """borrower constructor"""
        self.book_id = book_id
        self.email = email
        self.national_id = national_id
        self.borrower_id = borrower_id
        self.return_status = False

    def save_borrowed(self):
        """saves rented book to db"""
        db.session.add(self)
        db.session.commit()


class TokenBlacklisting(db.Model):
    """model handles blacklisting of tokens"""

    __tablename__ = "blacklisted_tokens"
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    token = db.Column(db.String(400), nullable=False)
    time_of_blacklisting = db.Column(
        db.TIMESTAMP, default=datetime.now, nullable=True)

    def __init__(self, token):
        """
        constructor receives token and asigns time for
        blacklisting when an object is created out of this class
        """
        self.token = token
        self.time_of_blacklisting = datetime.now()

    def save_token(self):
        """saves tokens to database"""
        db.session.add(self)
        db.session.commit()

    @staticmethod
    def verify_token(auth_token):
        """
        Checks if the token exist in the database,
        that is wether it is blacklisted or not.
        """
        blacklisted_token = TokenBlacklisting.query.filter_by(
            token=str(auth_token)).first()
        if blacklisted_token:
            return True
        return False

