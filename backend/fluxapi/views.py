from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, RiderRegistrationSerializer, CustomerRegistrationSerializer, UserProfileSerializer, OrderSerializer
from .permissions import IsSender, IsRider, IsCustomer
from .models import Order, RiderProfile


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


class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data.get("refresh")

            if not refresh_token:
                return Response(
                    {"error": "Refresh token is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Successfully logged out"},
                status=status.HTTP_205_RESET_CONTENT
            )
        except Exception as e:
            return Response(
                {"error": "Invalid or expired token"},
                status=status.HTTP_400_BAD_REQUEST
            )


class OrderCreationView(APIView):
    permission_classes = [IsSender]

    def post(self, request):
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            order = serializer.save(sender=request.user)
            return Response({'order': {
                'id': order.id,
                'package_description': order.package_description,
                'pickup_address': order.pickup_address,
                'delivery_address': order.delivery_address,
                'status': order.current_status
            }}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class AcceptOderView(APIView):
    permission_classes = [IsRider]

    def post(self, request, order_id):
        rider = request.user
        
        try:
            rider_profile = RiderProfile.objects.select_for_update().get(user=rider)
            if not rider_profile.is_available:
                return Response({'error': 'You already have an active order or marked as unavailable'}, status=status.HTTP_400_BAD_REQUEST) 
             
            order = Order.objects.select_for_update().get(id=order_id)
            if order.current_status != 'pending':
                return Response({'error': 'Order has been assigned to another rider'}, status=status.HTTP_400_BAD_REQUEST)
            
            order.rider = rider
            order.current_status = 'assigned'
            order.save()

            rider_profile.is_available = False
            rider_profile.active_order = order
            rider_profile.save()

            return Response({'message': 'Order successfully assigned to you'}, status=status.HTTP_200_OK)
        
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        

    class AvailableOrdersView(APIView):
        permission_classes = [IsRider]

        def get(self, request):
            orders = Order.objects.filter(current_status='pending')
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)