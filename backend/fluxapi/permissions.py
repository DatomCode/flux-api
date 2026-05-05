from rest_framework.permissions import BasePermission

# Custom permission classes to enforce role-based access control for different API endpoints based on the user's role (sender, rider, customer, admin)


class IsSender(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'sender'


class IsRider(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'rider'


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'customer'


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
