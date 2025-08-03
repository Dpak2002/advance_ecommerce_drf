from rest_framework import  permissions

class IsAdminUser(permissions.BasePermission):
    """
    Custom permission to only allow admin users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin


class IsCustomerUser(permissions.BasePermission):
    """
    Custom permission to only allow customer users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_customer
