#test_app.py
#coding:utf-8

#third party imports
from flask_testing import TestCase
import unittest
import json
#local import
from app import create_app, db

class TestBase(TestCase):
    """ common class"""
    def create_app(self):
         config_name = 'testing'
         self.app = create_app(config_name)
         self.client = self.app.test_client()
         return self.app
    
    def setUp(self):
        """ gets run before any test"""
        self.book={
            'author':'test author', 
            'title':'test title', 
            'publisher':'test publisher',
            'edition':'test edition',
            'category':'category', 
            'copies':10
        }

        self.admin = {
            'name':'collo',
            'email':'test@gmail.com',
            'national_id':000000,
            'admin':1,
            'password':'testpass',
            'confirm_pwd':'testpass'
        }
        self.user1 = {
            'name':'collo',
            'email':'test@gmail.com',
            'national_id':000000,
            'password':'testpass',
            'confirm_pwd':'testpass'
        }
        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

    def register(self):
        """helper function to issue token"""
        result = self.client.post(
        '/auth/api/v1/register',
        data = json.dumps(self.admin),
        content_type='application/json'
        )
        return result
    

class TestBook(TestBase):
    """tests admin methods"""
    def test_add_book(self):
        """test adding book"""
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        response = self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization': 'Bearer '+token
            },
            content_type='application/json'
        )
        self.assertTrue(response.status_code == 201)
    
    def test_non_admin_add_book(self):
        '''tests if not all users can add book'''
        result = self.client.post(
        '/auth/api/v1/register',
        data = json.dumps(self.user1),
        content_type='application/json'
        )
        token = json.loads(result.data.decode())['token']
        response = self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization': 'Bearer '+token
            },
            content_type='application/json'
        )
        self.assertFalse(response.status_code==201)

    def test_modify_book(self):
        '''tests modification of book'''
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        data = self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization':'Bearer ' +token
            },
            content_type='application/json'
        )
        self.assertEqual(data.status_code, 201)
        new_details={
            'new_author':'new authordetails', 
            'new_title':'test title1', 
            'new_publisher':'test publisher',
            'new_edition':'test edition',
            'new_category':'category', 
            'new_copies':5
        }
        result = self.client.put(
            '/api/v1/books/1',
            data = json.dumps(new_details),
            headers = {'authorization': 'Bearer '+ token},
            content_type='application/json'
        )
        res = json.loads(result.data.decode())
        self.assertIn('book details updated succesfully',res['message'])

    def test_delete_book(self):
        '''tests, book delete'''
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization':'Bearer ' +token
            },
            content_type='application/json'
        )
        result = self.client.delete(
             'api/v1/books/1',
             headers={
                 'authorization':'Bearer '+token
             },
             content_type='application/json'
        )
        res = json.loads(result.data.decode())
        self.assertIn('you have deleted: test title by test author', res['message'])

    def test_delete_wrong_token(self):
        '''tests delete with wrong token'''
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization':'Bearer ' +token
            },
            content_type='application/json'
        )
        result = self.client.delete(
             'api/v1/books/1',
             headers={
                 'authorization':'Bearer '+ 'jljbnjfbvjk.90qqnjsnjbk.jjbslkjs7sbh'
             },
             content_type='application/json'
        )
        res = json.loads(result.data.decode())
        self.assertIn('Invalid header padding', res['message'])

    def test_get_books(self):
        '''tests books retrival'''
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization':'Bearer ' +token
            },
            content_type='application/json'
        )
        books = self.client.get(
            'api/v1/books',
            content_type='application/json'
        )
        res = json.loads(books.data.decode())
        self.assertTrue(res['books_catalog'][0]['publisher'] == 'test publisher')

    def test_get_book(self):
        '''tests getting book by id'''
        signup = self.register()
        token = json.loads(signup.data.decode())['token']
        self.client.post(
            '/api/v1/books',
            data=json.dumps(self.book),
            headers = {
                'Authorization':'Bearer ' +token
            },
            content_type='application/json'
        )
        books = self.client.get(
            'api/v1/books/1',
            content_type='application/json'
        )
        res = json.loads(books.data.decode())
        self.assertIn('test publisher', res['publisher'])
        
if __name__ == '__main__':
    unittest.main()


