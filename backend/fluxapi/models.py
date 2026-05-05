from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

# Custom user model extending AbstractUser to include role and timestamps


class UserProfile(AbstractUser):
    ROLE = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('rider', 'Rider'),
        ('sender', 'Sender'),
    ]
    role = models.CharField(max_length=50, choices=ROLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Model for delivery addresses, allowing customers to have multiple saved addresses and also used for pickup/delivery locations in orders


class Address(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"

# Rider profile model to track rider-specific information such as availability and active order assignment


class RiderProfile(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='rider_profile')
    active_order = models.ForeignKey(
        'Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_rider')
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

# Customer profile model to track customer-specific information such as phone number and default delivery address, allowing for easier order creation and management


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        UserProfile, on_delete=models.CASCADE, related_name='customer_profile')
    default_delivery_address = models.ForeignKey(
        Address, on_delete=models.SET_NULL, null=True, blank=True, related_name='customer_default_address')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# Company model to allow senders to be associated with a company, and for orders to optionally be linked to a company for organizational purposes


class Company(models.Model):
    owner = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

# Order model to represent a delivery order, linking sender, customer, rider (if assigned), and company (if applicable), along with package details, addresses, and status tracking


class Order(models.Model):
    STATUS = [
        ('pending', 'Pending'),
        ('assigned', 'Assigned'),
        ('accepted', 'Accepted'),
        ('picked_up', 'Picked Up'),
        ('in_transit', 'In Transit'),
        ('arrived', 'Arrived'),
        ('delivered', 'Delivered'),
        ('completed', 'Completed'),
    ]

    sender = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='sent_orders')
    customer = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='received_orders')
    rider = models.ForeignKey(UserProfile, on_delete=models.CASCADE,
                              related_name='assigned_orders', null=True, blank=True)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    package_description = models.TextField()
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    current_status = models.CharField(
        max_length=50, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} from {self.sender.username} to {self.customer.username}"

# DeliveryCode model to generate and store unique codes for both rider and customer to confirm pickup and delivery, along with expiration time and confirmation status tracking


class DeliveryCode(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='delivery_codes')
    rider_code = models.CharField(max_length=6)
    customer_code = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    rider_confirmed = models.BooleanField(default=False)
    customer_confirmed = models.BooleanField(default=False)
    rider_confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery Codes for Order {self.order.id}"


# DeliveryStatusLog model to track the history of status changes for each order, including who made the change and when, for auditing and debugging purposes
class DeliveryStatusLog(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='status_logs')
    actor = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=50)
    to_status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status {self.to_status} for Order {self.order.id} at {self.timestamp}"
