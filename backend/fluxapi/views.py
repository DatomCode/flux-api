
from django.utils import timezone
import secrets
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserRegistrationSerializer, RiderRegistrationSerializer, CustomerRegistrationSerializer, UserProfileSerializer, OrderSerializer, RiderProfileSerializer
from .permissions import IsAdmin, IsSender, IsRider, IsCustomer
from .models import DeliveryCode, Order, RiderProfile
from datetime import timedelta
from django.db import transaction


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
        rider_profile = RiderProfile.objects.get(user=request.user)
        if not rider_profile.is_available:
            return Response({'error': 'You already have an active order or marked as unavailable'}, status=status.HTTP_400_BAD_REQUEST)
        orders = Order.objects.filter(
            current_status='pending').order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PickupOrderView(APIView):
    permission_classes = [IsRider]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)
            if order.rider != request.user:
                return Response({'error': 'You are not assigned to this order'}, status=status.HTTP_403_FORBIDDEN)
            if order.current_status != 'assigned':
                return Response({'error': f'Cannot pick up order. Current status is {order.current_status}.'},  status=status.HTTP_400_BAD_REQUEST)

            order.current_status = "picked_up"
            order.picked_up_at = timezone.now()
            order.save()
            return Response({'message': 'Order marked as picked up'}, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class ArriveOrderView(APIView):
    permission_classes = [IsRider]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.rider != request.user:
                return Response({'error': 'You are not assigned to this order'}, status=status.HTTP_403_FORBIDDEN)

            if order.current_status != 'in_transit':
                return Response({'error': 'Order is not in transit'}, status=status.HTTP_400_BAD_REQUEST)

            if DeliveryCode.objects.filter(order=order).exists():
                return Response({'error': 'Delivery codes already generated for this order'}, status=status.HTTP_400_BAD_REQUEST)

            order.current_status = 'arrived'
            order.save()

            delivery_code = DeliveryCode.objects.create(
                order=order,
                rider_code=secrets.token_hex(3),
                customer_code=secrets.token_hex(3),
                expires_at=timezone.now() + timedelta(minutes=15)
            )

            return Response({
                'message': 'Arrived at delivery location',
                'rider_code': delivery_code.rider_code,
                'customer_code': delivery_code.customer_code
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyCustomerView(APIView):
    permission_classes = [IsRider]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.rider != request.user:
                return Response({'error': 'You are not assigned to this order'}, status=status.HTTP_403_FORBIDDEN)

            if order.current_status != 'arrived':
                return Response({'error': 'Order is not at delivery location'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                delivery_code = DeliveryCode.objects.get(order=order)
            except DeliveryCode.DoesNotExist:
                return Response({'error': 'Delivery codes not found for this order'}, status=status.HTTP_404_NOT_FOUND)

            if delivery_code.customer_confirmed:
                return Response({'error': 'Customer code already verified'}, status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > delivery_code.expires_at:
                return Response({'error': 'Delivery codes have expired'}, status=status.HTTP_400_BAD_REQUEST)

            submitted_code = request.data.get('customer_code')
            if submitted_code != delivery_code.customer_code:
                return Response({'error': 'Invalid customer code'}, status=status.HTTP_400_BAD_REQUEST)

            delivery_code.customer_confirmed = True
            delivery_code.customer_confirmed_at = timezone.now()
            delivery_code.save()

            return Response({'message': 'Customer code verified. Share your rider code with the customer.'}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class VerifyRiderView(APIView):

    permission_classes = [IsCustomer]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            if order.current_status != 'arrived':
                return Response({'error': 'Order is not at delivery location'}, status=status.HTTP_400_BAD_REQUEST)

            try:
                delivery_code = DeliveryCode.objects.get(order=order)
            except DeliveryCode.DoesNotExist:
                return Response({'error': 'Delivery codes not found for this order'}, status=status.HTTP_404_NOT_FOUND)

            if not delivery_code.customer_confirmed:
                return Response({'error': 'Rider must verify customer code first'}, status=status.HTTP_400_BAD_REQUEST)

            if delivery_code.rider_confirmed:
                return Response({'error': 'Rider code already verified'}, status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > delivery_code.expires_at:
                return Response({'error': 'Delivery codes have expired'}, status=status.HTTP_400_BAD_REQUEST)

            submitted_code = request.data.get('rider_code')
            if submitted_code != delivery_code.rider_code:
                return Response({'error': 'Invalid rider code'}, status=status.HTTP_400_BAD_REQUEST)
            with transaction.atomic():
                delivery_code.rider_confirmed = True
                delivery_code.rider_confirmed_at = timezone.now()
                delivery_code.save()

                order.current_status = 'delivered'
                order.save()

                rider_profile = RiderProfile.objects.get(user=order.rider)
                rider_profile.is_available = True
                rider_profile.active_order = None
                rider_profile.save()

            return Response({'message': 'Delivery confirmed. Order complete.'}, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class RiderAvailabilitySwitchView(APIView):
    permission_classes = [IsRider]

    def post(self, request):
        rider_profile = RiderProfile.objects.get(user=request.user)
        if rider_profile.active_order:
            return Response({'error': 'Cannot change availability while having an active order'}, status=status.HTTP_400_BAD_REQUEST)
        rider_profile.is_available = not rider_profile.is_available
        rider_profile.save()
        return Response({'message': f'Availability set to {rider_profile.is_available}'}, status=status.HTTP_200_OK)
    
class FetchRiderProfileView(APIView):
    permission_classes = [IsRider]

    def get(self, request):
        rider_profile = RiderProfile.objects.get(user=request.user)
        serializer = RiderProfileSerializer(rider_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FetchRiderOrderDetailsView(APIView):
    permission_classes = [IsRider]

    def get(self, request):
        orders = Order.objects.filter(rider=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FetchSenderOrdersDetailsView(APIView):
    permission_classes = [IsSender]

    def get(self, request):
        orders = Order.objects.filter(sender=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FetchSenderOrderWellDetailsView(APIView):
    permission_classes = [IsSender]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, sender=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)
        
        
class FetchCustomerOrdersDetailsView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request):
        orders = Order.objects.filter(customer=request.user).order_by('-created_at')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class FetchCustomerOrderWellDetailsView(APIView):
    permission_classes = [IsCustomer]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, customer=request.user)
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class AdminOrdersListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        orders = Order.objects.all().order_by('-created_at')

       
        status_filter = request.query_params.get('status')
        if status_filter:
            orders = orders.filter(current_status=status_filter)

        
        date_filter = request.query_params.get('date')
        if date_filter:
            orders = orders.filter(created_at__date=date_filter)

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AdminRidersListView(APIView):
    permission_classes = [IsAdmin]

    def get(self, request):
        riders = RiderProfile.objects.select_related('user').all().order_by('-created_at')
        serializer = RiderProfileSerializer(riders, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AdminOrderStateOverrideView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id)

            new_status = request.data.get('current_status')
            if not new_status:
                return Response({'error': 'Status is required'}, status=status.HTTP_400_BAD_REQUEST)

            valid_statuses = ['pending', 'assigned', 'accepted', 'picked_up', 'in_transit', 'arrived', 'delivered', 'completed']
            if new_status not in valid_statuses:
                return Response({'error': f'Invalid status. Valid options are: {valid_statuses}'}, status=status.HTTP_400_BAD_REQUEST)

            old_status = order.current_status
            order.current_status = new_status
            order.save()

            return Response({
                'message': f'Order status updated',
                'order_id': order.id,
                'old_status': old_status,
                'new_status': order.current_status
            }, status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)


class DeliveriesDetailsView(APIView):
    permission_classes = [IsRider, IsSender, IsCustomer, IsAdmin]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id = order_id)
            if request.user == IsAdmin:
                pass
        except Order.DoesNotExist:
            return Response({'error': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)



