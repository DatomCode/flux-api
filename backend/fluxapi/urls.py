from django.urls import path
from .views import SenderRegistrationView

urlpatterns = [
    # auth endpoint
    path("auth/sender/",SenderRegistrationView.as_view(), name="sender-registration"),
]
