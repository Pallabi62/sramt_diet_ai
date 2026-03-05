import unittest
from app import app, db
from models import User
import os

class DietPlannerTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.client = app.test_client()
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()

    def test_index(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'SmartDiet', response.data)

    def test_register_login(self):
        # Register
        response = self.client.post('/register', data=dict(
            username='testuser',
            email='test@example.com',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # Verify redirect to login or success message
        self.assertIn(b'Registration successful', response.data)

        # Login
        response = self.client.post('/login', data=dict(
            username='testuser',
            password='password'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login successful', response.data)

if __name__ == '__main__':
    unittest.main()
