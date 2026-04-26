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
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(
            '/api/auth/login/',
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
            '/api/auth/login/',
            data=json.dumps({'username': 'testsender', 'password': 'testpass123'}),
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
            '/api/deliveries/',
            data=json.dumps(data),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()['order']['status'], 'pending')

class AvailableOrdersTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.rider_user = UserProfile.objects.create_user(
            username='testrider',
            email='rider@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Rider',
            role='rider'
        )
        RiderProfile.objects.create(user=self.rider_user, is_available=True)
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'testrider', 'password': 'testpass123'}),
            content_type='application/json'
        )
        self.token = response.json()['access']

    def test_rider_can_see_available_orders(self):
        response = self.client.get(
            '/api/deliveries/available/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


class RiderAcceptOrderTest(TestCase):
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
        self.rider_user = UserProfile.objects.create_user(
            username='testrider',
            email='rider@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Rider',
            role='rider'
        )
        self.rider_profile = RiderProfile.objects.create(
            user=self.rider_user,
            is_available=True
        )
        self.order = Order.objects.create(
            sender=self.sender,
            customer=self.sender,
            package_description='Test package',
            pickup_address='123 Pickup Street',
            delivery_address='456 Delivery Avenue',
            current_status='pending'
        )
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'testrider', 'password': 'testpass123'}),
            content_type='application/json'
        )
        self.token = response.json()['access']

    def test_rider_can_accept_order(self):
        response = self.client.post(
            f'/api/deliveries/{self.order.id}/accept/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.current_status, 'assigned')

    def test_unavailable_rider_cannot_accept_order(self):
        self.rider_profile.is_available = False
        self.rider_profile.save()
        response = self.client.post(
            f'/api/deliveries/{self.order.id}/accept/',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeliveryConfirmTest(TestCase):
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
        self.rider_user = UserProfile.objects.create_user(
            username='testrider',
            email='rider@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Rider',
            role='rider'
        )
        self.rider_profile = RiderProfile.objects.create(
            user=self.rider_user,
            is_available=False
        )
        self.order = Order.objects.create(
            sender=self.sender,
            customer=self.sender,
            package_description='Test package',
            pickup_address='123 Pickup Street',
            delivery_address='456 Delivery Avenue',
            current_status='arrived',
            rider=self.rider_user
        )
        self.delivery_code = DeliveryCode.objects.create(
            order=self.order,
            rider_code='abc123',
            customer_code='def456',
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'testrider', 'password': 'testpass123'}),
            content_type='application/json'
        )
        self.token = response.json()['access']

    def test_rider_can_verify_customer_code(self):
        response = self.client.post(
            f'/api/deliveries/{self.order.id}/confirm/',
            data=json.dumps({'customer_code': 'def456'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.delivery_code.refresh_from_db()
        self.assertTrue(self.delivery_code.customer_confirmed)


class AdminOrderOverrideTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.admin = UserProfile.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Admin',
            role='admin'
        )
        self.sender = UserProfile.objects.create_user(
            username='testsender',
            email='sender@test.com',
            password='testpass123',
            first_name='Test',
            last_name='Sender',
            role='sender'
        )
        self.order = Order.objects.create(
            sender=self.sender,
            customer=self.sender,
            package_description='Test package',
            pickup_address='123 Pickup Street',
            delivery_address='456 Delivery Avenue',
            current_status='pending'
        )
        response = self.client.post(
            '/api/auth/login/',
            data=json.dumps({'username': 'testadmin', 'password': 'testpass123'}),
            content_type='application/json'
        )
        self.token = response.json()['access']

    def test_admin_can_override_order_status(self):
        response = self.client.post(
            f'/api/admin/orders/{self.order.id}/override/',
            data=json.dumps({'current_status': 'delivered'}),
            content_type='application/json',
            HTTP_AUTHORIZATION=f'Bearer {self.token}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.order.refresh_from_db()
        self.assertEqual(self.order.current_status, 'delivered')