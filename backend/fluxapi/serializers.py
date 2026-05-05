from rest_framework import serializers
from .models import UserProfile, RiderProfile, CustomerProfile, Order
from django.contrib.auth.hashers import make_password
import secrets



# User registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'password', 'created_at', 'updated_at', 'role']
        extra_kwargs = {'password': {'write_only': True}}

    # Add validation to prevent users from registering as admin
    def validate_role(self, value):
        if value == 'admin':
            raise serializers.ValidationError("Cannot register as admin.")
        return value
    
    # create method to handle user creation and associated profile creation
    def create(self, validated_data):

        role = validated_data.get('role')

        user = UserProfile.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            role = role
        )
        # Automatically create associated profile based on role
        if role == 'rider':
            RiderProfile.objects.create(
                user=user,
                is_available=True
            )
        elif role == 'customer':
            CustomerProfile.objects.create(
                user=user,
                phone_number='',
                default_delivery_address=None
            )

        return user
    

# Profile serializer to return users details along with role-specific profile information

#returns sender and admin details
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'role', 'created_at', 'updated_at']

#  returns rider details along with availability status
class RiderProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiderProfile
        fields = ['id', 'user', 'is_available', 'created_at', 'updated_at']

# returns customer details along with phone number and default delivery address
class CustomerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerProfile
        fields = ['id', 'user', 'phone_number', 'default_delivery_address', 'created_at', 'updated_at']



# Serializer for creating a delivery order, allowing either customer phone or email for ghost user creation if the customer does not exist

class OrderSerializer(serializers.ModelSerializer):
    # Allow either phone or email for customer identification
    customer_phone = serializers.CharField(required=False)
    customer_email = serializers.EmailField(required=False)

    class Meta:
        model = Order
        fields = ['id', 'package_description', 'pickup_address', 
          'delivery_address', 'company', 'customer_phone', 'customer_email'] 
        
     # Add validation to ensure at least one of customer_phone or customer_email is provided   
    def validate(self, data):
        if not data.get('customer_phone') and not data.get('customer_email'):
            raise serializers.ValidationError(
                "Provide either customer phone number or email."
            )
        return data
        # Override create method to handle ghost user creation if customer does not exist, and associate the order with the correct sender and customer
    def create(self, validated_data):
        customer_phone = validated_data.pop('customer_phone', None)
        customer_email = validated_data.pop('customer_email', None)
        sender = validated_data.pop('sender')

        customer = None
    # First try to find existing customer by phone, then by email. If neither exists, create a ghost user and profile
        if customer_phone:
            try:
                customer_profile = CustomerProfile.objects.get(phone_number=customer_phone)
                customer = customer_profile.user
            except CustomerProfile.DoesNotExist:
                pass
               
        if customer is None and customer_email:
            try:
                customer_profile = CustomerProfile.objects.get(user__email=customer_email)
                customer = customer_profile.user
            except CustomerProfile.DoesNotExist:
                pass

        # If customer still doesn't exist, create a ghost user and profile, and log a notification (stubbed for now)
        if customer is None:
            
            ghost_user = UserProfile.objects.create_user(
                username=customer_phone or customer_email,
                email=customer_email or '',
                password=make_password(secrets.token_hex(16)),
                role='customer',
                first_name='',
                last_name=''
            )
            CustomerProfile.objects.create(
                user=ghost_user,
                phone_number=customer_phone or '',
                default_delivery_address=None
            )
            customer = ghost_user

            print(f"[STUB] Notify {customer_phone or customer_email}: You have a delivery coming. Sign up on Flux to track it.")

        order = Order.objects.create(
        sender=sender,
        customer=customer,
        current_status='pending',
        **validated_data
        )

        return order
