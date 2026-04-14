from django.urls import path
from .views import SenderRegistrationView, RiderRegistrationView, CustomerRegistrationView, UserProfileView, OrderCreationView, LogoutView, AcceptOderView, AvailableOrdersView
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    # auth endpoint
    path("auth/sender/",SenderRegistrationView.as_view(), name="sender-registration"),
    path("auth/rider/",RiderRegistrationView.as_view(), name="rider-registration"),
    path("auth/customer/",CustomerRegistrationView.as_view(), name="customer-registration"),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    

    # delivery endpoints
    path("deliveries/", OrderCreationView.as_view(), name="order-create"),
    path("deliveries/<int:order_id>/accept/", AcceptOderView.as_view(), name="order-accept"),
    path("deliveries/available/", AvailableOrdersView.as_view(), name="available-orders"),

]
