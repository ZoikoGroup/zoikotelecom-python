from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import ContactMessage

class ContactMessageAPITests(APITestCase):
    def setUp(self):
        # The contact app url is prefixed with /api/contact/ via core/urls.py
        # and has name='contact-us' inside apps/contact/urls.py.
        # Since it's included without an app namespace, its name is just 'contact-us'.
        self.url = '/api/contact/contact-us/'

    def test_contact_us_success(self):
        """Test successful contact form submission with standard values."""
        data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "subject": "General Support",
            "message": "This is a valid test message from a user."
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.first_name, "John")
        self.assertEqual(msg.last_name, "Doe")
        self.assertEqual(msg.phone, "1234567890")

    def test_contact_us_long_phone_success(self):
        """Test successful submission with a long/international phone number (up to 20 chars)."""
        data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "email": "jane.smith@example.com",
            "phone": "+44 7123 456 789",  # 16 characters
            "subject": "BT Broadband",
            "message": "Testing the extended phone character field limit."
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["success"])
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        msg = ContactMessage.objects.first()
        self.assertEqual(msg.phone, "+44 7123 456 789")

    def test_contact_us_missing_fields(self):
        """Test validation error for missing fields."""
        data = {
            "first_name": "",
            "last_name": "Doe",
            "email": "invalid-email",
            "phone": "12345",
            "subject": "",
            "message": ""
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])
        self.assertIn("first_name", response.data["errors"])
        self.assertIn("email", response.data["errors"])
