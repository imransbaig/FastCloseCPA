import unittest
from app import app
from extensions import db
from models import User, Consultation
from datetime import datetime

class TestApp(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test"""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        app.config['SENDGRID_API_KEY'] = 'dummy_key'  # Mock SendGrid API key for testing
        self.client = app.test_client()

        # Create application context
        self.app_context = app.app_context()
        self.app_context.push()

        # Create all database tables
        db.create_all()

    def tearDown(self):
        """Clean up test environment after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        """Test if home page loads correctly"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Fast Close AI CPAs', response.data)

    def test_contact_page_get(self):
        """Test if contact page loads correctly"""
        response = self.client.get('/contact')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Contact Us', response.data)

    def test_contact_form_submission(self):
        """Test contact form submission"""
        test_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'service_type': 'Tax Preparation',
            'message': 'Test message'
        }
        response = self.client.post('/contact', data=test_data, follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # Verify consultation was saved
        consultation = Consultation.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(consultation)
        self.assertEqual(consultation.name, 'Test User')

    def test_services_page(self):
        """Test if services page loads correctly"""
        response = self.client.get('/services')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Our Services', response.data)

if __name__ == '__main__':
    unittest.main()