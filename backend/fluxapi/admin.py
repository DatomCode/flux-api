from django.contrib import admin
from .models import UserProfile, Address, RiderProfile, CustomerProfile, Company, Order, DeliveryCode, DeliveryStatusLog

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(RiderProfile)
admin.site.register(CustomerProfile)
admin.site.register(Company)
admin.site.register(Order)
admin.site.register(DeliveryCode)
admin.site.register(DeliveryStatusLog)
