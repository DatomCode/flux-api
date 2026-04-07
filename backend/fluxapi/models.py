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



