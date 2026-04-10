from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile, RiderProfile, CustomerProfile
from .serializers import UserRegistrationSerializer, RiderRegistrationSerializer, CustomerRegistrationSerializer


# Create your views here.


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }




class SenderRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='sender')
            tokens = get_tokens_for_user(user)
            return Response({'user': {
                {'id': user.id, 
                 'email': user.email, 
                 'username': user.username, 
                 'role': user.role}
                    **tokens}}, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)


