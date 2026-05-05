from rest_framework.throttling import UserRateThrottle, AnonRateThrottle

# Define custom throttling classes for different API endpoints

# Throttle for login attempts, allowing a certain number of attempts per minute from anonymous users
class LoginThrottle(AnonRateThrottle):
    scope = 'login'

# Throttle for delivery creation, allowing a certain number of deliveries to be created per user per minute
class DeliveryCreateThrottle(UserRateThrottle):
    scope = 'delivery_create'
# Throttle for state transitions, allowing a certain number of state changes per user per minute
class StateTransitionThrottle(UserRateThrottle):
    scope = 'state_transition'
