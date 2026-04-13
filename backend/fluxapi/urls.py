from django.urls import path
from .views import SenderRegistrationView, RiderRegistrationView, CustomerRegistrationView, UserProfileView, OrderCreationView
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    # auth endpoint
    path("auth/sender/",SenderRegistrationView.as_view(), name="sender-registration"),
    path("auth/rider/",RiderRegistrationView.as_view(), name="rider-registration"),
    path("auth/customer/",CustomerRegistrationView.as_view(), name="customer-registration"),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    

    # order endpoints
    path("orders/create/", OrderCreationView.as_view(), name="order-create"),
]
