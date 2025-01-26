
import unittest
from app import app
from extensions import db

class TestApp(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        with app.app_context():
            db.create_all()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_contact_page(self):
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
