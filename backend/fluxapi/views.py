from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, RiderRegistrationSerializer, CustomerRegistrationSerializer, UserProfileSerializer, OrderSerializer
from .permissions import IsSender, IsRider, IsCustomer


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
                'id': user.id, 
                'email': user.email, 
                'username': user.username, 
                'role': user.role},
                    **tokens}, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)

class RiderRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RiderRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='rider')
            tokens = get_tokens_for_user(user)
            return Response({'user': {
                'id': user.id, 
                'email': user.email, 
                'username': user.username, 
                'role': user.role},
                    **tokens}, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    
class CustomerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save(role='customer')
            tokens = get_tokens_for_user(user)
            return Response({'user': {
                'id': user.id, 
                'email': user.email, 
                'username': user.username, 
                'role': user.role},
                    **tokens}, status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status.HTTP_400_BAD_REQUEST)
    



class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        user = request.user
        serializer = UserProfileSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class OrderCreationView(APIView):
    permission_classes = [IsSender]
    

    def post(self, request): 
        serializer = OrderSerializer(data = request.data)
        if serializer.is_valid():
            order = serializer.save(sender=request.user)
            return Response({'order': {
                'id': order.id, 
                'pickup_address': order.pickup_address, 
                'delivery_address': order.delivery_address, 
                'status': order.current_status
                }}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)