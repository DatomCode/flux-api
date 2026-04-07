from django.db import models

# Create your models here.


class User(models.Model):

    ROLE = {
        'admin': 'Admin',
        'customer': 'Customer',
        'rider': 'Rider',
        'sender': 'Sender'
    }

    firstname = models.CharField(max_length=100)
    lastname = models.CharField(max_length=100)
    username = models.CharField(max_length=100)
    email = models.EmailField()
    role = models.CharField(max_length=50, choices=ROLE.items())
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class Delivery(models.Model):

    STATE = {
        'pending': 'Pending',
        'assigned': 'Assigned',
        'accepted': 'Accepted',
        'picked_up': 'Picked Up',
        'in_transit': 'In Transit',
        'arrived': 'Arrived',
        'delivered': 'Delivered',
        'completed': 'completed'
    }

    sender = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='sent_deliveries')
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='received_deliveries')
    rider = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name='assigned_deliveries', null=True, blank=True)
    package_description = models.TextField()
    pickup_address = models.CharField(max_length=255)
    delivery_address = models.CharField(max_length=255)
    current_state = models.CharField(
        max_length=50, choices=STATE.items(), default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Delivery {self.id} from {self.sender.username} to {self.customer.username}"


class DeliveryLog(models.Model):
    delivery_id = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name='logs')
    changed_by = models.ForeignKey(User, on_delete=models.CASCADE)
    from_state = models.CharField(
        max_length=50, choices=Delivery.STATE.items())
    to_state = models.CharField(max_length=50, choices=Delivery.STATE.items())
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Log for Delivery {self.delivery_id.id}: {self.from_state} → {self.to_state}"


class Confirmation(models.Model):
    delivery_id = models.ForeignKey(
        Delivery, on_delete=models.CASCADE, related_name='confirmations')
    code_a = models.CharField(max_length=6)
    code_b = models.CharField(max_length=6)
    rider_confirmed = models.BooleanField(default=False)
    customer_confirmed = models.BooleanField(default=False)
    rider_confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField(null=False, blank=False)

    def __str__(self):
        return f"Confirmation for Delivery {self.delivery_id.id}"
