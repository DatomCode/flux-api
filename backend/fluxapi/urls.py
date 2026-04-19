from django.urls import path
from .views import UserProfileView, UserRegistrationView, OrderCreationView, LogoutView, AcceptOderView, AvailableOrdersView, PickupOrderView, VerifyCustomerView, VerifyRiderView, FetchRiderOrderDetailsView, FetchRiderProfileView, UserLoginView, RiderAvailabilitySwitchView, FetchSenderOrdersDetailsView, FetchSenderOrderWellDetailsView, FetchCustomerOrdersDetailsView, FetchCustomerOrderWellDetailsView, AdminRidersListView, AdminOrdersListView, AdminOrderStateOverrideView, DeliveriesDetailsView
from rest_framework_simplejwt.views import TokenRefreshView



urlpatterns = [
    # auth endpoint
    path('auth/register/', UserRegistrationView.as_view(), name='auth_register'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('auth/login/', UserLoginView.as_view(), name='token_obtain_pair'),
    path('auth/logout/', LogoutView.as_view(), name='auth_logout'),
    path("profile/", UserProfileView.as_view(), name="user-profile"),
    

    # delivery endpoints
    path("deliveries/", OrderCreationView.as_view(), name="order-create"),
    path("deliveries/<int:order_id>/accept/", AcceptOderView.as_view(), name="order-accept"),
    path("deliveries/available/", AvailableOrdersView.as_view(), name="available-orders"),


    path("deliveries/<int:order_id>/pickup/", PickupOrderView.as_view(), name="order-pickup"),
    path("deliveries/<int:order_id>/customer/confirm/", VerifyCustomerView.as_view(), name="customer-confirm"),
    path("deliveries/<int:order_id>/rider/confirm/", VerifyRiderView.as_view(), name="rider-confirm"),

    # rider endpoints
    path("rider/orders/", FetchRiderOrderDetailsView.as_view(), name="fetch-order-details"),
    path("rider/availability/", RiderAvailabilitySwitchView.as_view(), name="rider-availability-switch"),

    # sender endpoints
    path("sender/orders/", FetchSenderOrdersDetailsView.as_view(), name="fetch-sender-orders"),
    path("sender/orders/<int:order_id>/details/", FetchSenderOrderWellDetailsView.as_view(), name="fetch-sender-order-details"),

    # customer endpoints
    path("customer/orders/", FetchCustomerOrdersDetailsView.as_view(), name="fetch-customer-orders"),
    path("customer/orders/<int:order_id>/details/", FetchCustomerOrderWellDetailsView.as_view(), name="fetch-customer-order-details"),
    
    # admin endpoints
    path("admin/riders/", AdminRidersListView.as_view(), name="admin-riders-list"),
    path("admin/orders/", AdminOrdersListView.as_view(), name="admin-orders-list"), 
    path("admin/orders/<int:order_id>/override/", AdminOrderStateOverrideView.as_view(), name="admin-order-override"),

    # deliveries details endpoint
    path("deliveries/<int:order_id>/details/", DeliveriesDetailsView.as_view(), name="deliveries-details"),
]
