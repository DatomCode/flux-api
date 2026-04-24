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


class UserLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserProfile.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            role='sender'
        )

    def test_user_can_login(self):
        data = {
            'email': 'test@test.com',
            'password': 'testpass123'
        }
        response = self.client.post(
            '/fluxapi/auth/login/',
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.json())
        self.assertIn('refresh', response.json())


class DeliveryCreationTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.sender = UserProfile.objects.create_user(
            username='testsender',
            email='sender@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Sender',
            role='sender'
        )
        # login to get token
        response = self.client.post(
            '/fluxapi/auth/login/',
            data=json.dumps({'email': 'sender@test.com', 'password': 'testpass123'}),
            content_type='application/json'
        )
        self.token = response.json()['access']

    def test_sender_can_create_delivery(self):
        data = {
            'package_description': 'Test package',
            'pickup_address': '123 Pickup Street',
            'delivery_address': '456 Delivery Avenue',
            'customer_email': 'customer@test.com'
        }
        response = self.client.post(
            '/fluxapi/deliveries/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['order']['status'], 'pending')