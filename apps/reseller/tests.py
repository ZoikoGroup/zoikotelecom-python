from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from .models import ResellerApplication
import datetime
from unittest.mock import patch

class ResellerAPITests(APITestCase):
    def setUp(self):
        self.url = reverse('apply_reseller')
        self.valid_payload = {
            "company_name": "Test Company Ltd",
            "contact_name": "John Doe",
            "position": "Director",
            "email": "john.doe@testcompany.com",
            "phone": "+447123456789",
            "website": "https://testcompany.com",
            "address": "123 Test Street",
            "city": "London",
            "post_code": "EC1A 1BB",
            "country": "United Kingdom",
            "services_of_interest": ["EE Mobile Plans", "BT Broadband"],
            "full_name": "John Doe",
            "digital_signature": "John Doe",
            "signature_date": str(datetime.date.today())
        }
        self.invalid_payload = {
            "company_name": "",
            "contact_name": "John Doe",
            "email": "invalid-email",
            "phone": ""
        }

    @patch('apps.reseller.views.send_reseller_email')
    def test_apply_reseller_success(self, mock_send_email):
        response = self.client.post(self.url, self.valid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['message'], "Your reseller application has been submitted successfully.")
        
        # Verify email task was triggered
        mock_send_email.assert_called_once()
        
        # Verify db entry
        self.assertEqual(ResellerApplication.objects.count(), 1)
        app = ResellerApplication.objects.first()
        self.assertEqual(app.company_name, "Test Company Ltd")
        self.assertEqual(app.services_of_interest, ["EE Mobile Plans", "BT Broadband"])

    def test_apply_reseller_invalid_data(self):
        response = self.client.post(self.url, self.invalid_payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
        self.assertIn('company_name', response.data['errors'])
        self.assertIn('email', response.data['errors'])
        self.assertIn('phone', response.data['errors'])
        self.assertEqual(ResellerApplication.objects.count(), 0)
