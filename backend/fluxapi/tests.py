from django.test import TestCase, Client
from rest_framework import status
from .models import UserProfile, RiderProfile, Order, DeliveryCode
from django.utils import timezone
from datetime import timedelta
import json


# Create your tests here.

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_rider_can_register(self):
        data = {
            'username': 'testrider',
            'email': 'rider@test.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'Rider',
            'role': 'rider'
        }
        response = self.client.post(
            '/api/auth/register/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['user']['role'], 'rider')