from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class LoginThrottle(AnonRateThrottle):
    scope = 'login'


class DeliveryCreateThrottle(UserRateThrottle):
    scope = 'delivery_create'


class StateTransitionThrottle(UserRateThrottle):
    scope = 'state_transition'