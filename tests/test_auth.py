#tests/test_user.py

#third party imports
from flask_testing import TestCase
from flask import request
import unittest 
import json

#local imports
from app import create_app,db
from app.models import User,TokenBlacklisting

class Testbase(TestCase):
    """parent class"""
    def create_app(self):
        self.app = create_app('testing')
        return self.app

    def setUp(self):
        self.client = self.app.test_client()
        self.register_user={
            'name':'jane',
            'email':'jane@gmail.com',
            'national_id':30787373,
            'password':'testpass',
            'confirm_pwd':'testpass'
        }
        self.login_user={
            'email':'jane@gmail.com',
            'password':'testpass'
        }
        with self.app.app_context():
            db.session.close()
            db.drop_all()
            db.create_all()

class TestAuth(Testbase):
    """tests user authentication methods"""
    def test_registration(self):
        """test tregistaration"""
        response = self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code,201)
    
    def test_login(self):
        """test login"""
        self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        ) 
        response = self.client.post(
            'auth/api/v1/login',
            data=json.dumps(self.login_user),
            content_type='application/json'
        )     
        self.assertEqual(response.status_code,200) 
    
    def test_reset_password(self):
        """tests if a user can change password"""
        response = self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        )
        self.assertEqual(response.status_code,201)

        new_details = {
            'email':'jane@gmail.com',
            'new_password':'new_pass'
        }
        response = self.client.post(
            '/api/auth/reset-password',
            data=json.dumps(new_details),
            content_type='application/json'
        )
        self.assertIn('password reset successful', str(response.data))
        self.assertEqual(response.status_code,201)

    def test_logout(self):
        """tests_user logout"""
        
        register = self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        )   
        self.assertEqual(register.status_code,201) 
        self.data_ = json.loads(register.data.decode())
        self.assertEqual(self.data_['message'],'registration successfull')

        logout = self.client.post(
            'auth/api/v1/logout',
            headers={
                'Authorization':'Bearer ' + json.loads(
                    register.data.decode()
                )['token'],
            },
            content_type='application/json'
        )
        res = json.loads(logout.data.decode())
        self.assertIn('see you soon jane, you have successfully logged out', res['message'])

    def test_logout_tokenles(self):
        '''tests login with no token'''
        logout = self.client.post(
            'auth/api/v1/logout',
            content_type='application/json'
        )
        self.assertEqual(logout.status_code,403)

    def test_register_once(self):
        '''tests register with same email is allowed once'''
        self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        )
        register = self.client.post(
            'auth/api/v1/register',
            data=json.dumps(self.register_user),
            content_type='application/json'
        )
        res = json.loads(register.data.decode())
        self.assertIn('user already registred, login',res['message'])
        

if __name__ == "__main__":
    unittest.main()
