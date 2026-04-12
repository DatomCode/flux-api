from rest_framework.permissions import BasePermission


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
