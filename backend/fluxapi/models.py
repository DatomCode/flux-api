from django.db import models


class UserProfile(models.Model):
    ROLE = [
        ('admin', 'Admin'),
        ('customer', 'Customer'),
        ('rider', 'Rider'),
        ('sender', 'Sender'),
    ]

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=50, choices=ROLE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username

class RiderProfile(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='rider_profile')
    active_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, related_name='active_rider')
    is_available = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

class CustomerProfile(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='customer_profile')
    default_delivery_address = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Company(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='companies')
    name = models.CharField(max_length=255)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class Address(models.Model):
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.address}, {self.city}, {self.state}"


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

    sender = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_orders')
    customer = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_orders')
    rider = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='assigned_orders', null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='orders')
    delivery_address = models.ForeignKey(Address, on_delete=models.CASCADE, related_name='orders')
    package_description = models.TextField()
    pickup_address = models.CharField(max_length=255)
    delivery_address_text = models.CharField(max_length=255)
    current_status = models.CharField(max_length=50, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.id} from {self.sender.username} to {self.customer.username}"


class DeliveryCode(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_codes')
    code_a = models.CharField(max_length=6)
    code_b = models.CharField(max_length=6)
    expires_at = models.DateTimeField()
    rider_confirmed = models.BooleanField(default=False)
    customer_confirmed = models.BooleanField(default=False)
    rider_confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Delivery Codes for Order {self.order.id}"

class DeliveryStatusLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_logs')
    actor = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='status_logs')
    from_status = models.CharField(max_length=50)
    to_status = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Status {self.to_status} for Order {self.order.id} at {self.timestamp}"
