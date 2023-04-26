from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admin users to modify an object,
    but allow all users to view it.
    """

    def has_permission(self, request, view):
        """has_permission method is called when checking permissions for the entire view"""
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

    def has_object_permission(self, request, view, obj):
        """called when checking permissions for an individual object."""
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff
