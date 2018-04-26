[![Build Status](https://travis-ci.org/TheSteelGuy/Hello-BooksAPI.svg?branch=master)](https://travis-ci.org/TheSteelGuy/Hello-BooksAPI)


# Hello-Books app

### Introduction
The application allows admin(s) to manage the library resources(books) efficiently.
Registered/authenticated users can borrow,return and view the books they owe the library.
Anybody can see the list of available books.


#### Getting Started


#### Usage
With the app Hello-Books:
#### Admin can:
* Add a book 
* Update book information/details
* View users who owns the library book(s)
* View all books in the library
* Remove a book from the list of available books 

#### Registered user can:
* Create an account
* Login into the account
* Logout
* Borrow books
* View books owed to the library
* Return a book


#### Setting
* First install the virtual environment globally `sudo pip instal virtualenv`
* create the virtual enviroment `virtualenv --python=python3 myenv`
* change directory to myenv
* activate virtual environment `source myenv/bin/activate`
* clone the repo by running on terminal `git clone https://github.com/TheSteelGuy/Hello-BooksAPI.git `
* run pip install requirements.txt
* change directory to the repo `cd /Hell-BooksAPI`
* type`export APP_SETTINGS=development` 
* `run python manage.py`
* `run python manage.py init`
* `run python manage.py migrate`
* `run python manage.py upgrade`

# test endpoints using postman



#### How to run flask
* Run  `python run.py`

#### Testing:
* Install nosetests `pip install nose`

* Run the tests `nosetests `
#### Flask API endpoints

| Endpoints                                       |       Functionality                  |
| ------------------------------------------------|:------------------------------------:|
| `POST /api/v1/auth/register`                    |  Creates a user account              |
| `POST /api/v1/auth/reset-password`              |  Password reset                      |
| `POST /api/v1/auth/login`                       |  login a user                        |   
| `GET  /api/v1/books/<bookId>                    |  Get a book                          |
| `GET  /api/v1/books`                            |  Retrieves all books                 |
| `PUT /api/v1/books/<bookId>`                    |  modify a book’s information         |
| `DELETE /api/v1/books/<bookId>`                 |  Remove a book                       |
| `POST  /api/v1/users/books/<bookId>`            |  Borrow book                         |
|` POST /api/v1/logout`                           |  logs out a user                      |
