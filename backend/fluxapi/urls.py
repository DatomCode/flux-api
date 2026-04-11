from django.urls import path
from .views import SenderRegistrationView, RiderRegistrationView, CustomerRegistrationView, UserProfileView

urlpatterns = [
    # auth endpoint
    path("auth/sender/",SenderRegistrationView.as_view(), name="sender-registration"),
    path("auth/rider/",RiderRegistrationView.as_view(), name="rider-registration"),
    path("auth/customer/",CustomerRegistrationView.as_view(), name="customer-registration"),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
]
