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


class IsDoctorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.profile.user_type == 'doctor'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.profile.user_type == 'doctor'


class IsAgentOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.profile.user_type == 'agent'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.profile.user_type == 'agent'


class IsPatientOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated and request.user.profile.user_type == 'patient'

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.profile.user_type == 'patient'


class IsAgent(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.user_type == 'agent'

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.profile.user_type == 'agent'


class IsDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.user_type == 'doctor'

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.profile.user_type == 'doctor'


class IsPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.profile.user_type == 'patient'

    def has_object_permission(self, request, view, obj):
        return request.user and request.user.profile.user_type == 'patient'


class IsAgentOrDoctor(BasePermission):
    def has_permission(self, request, view):
        return request.user and (
                request.user.profile.user_type == 'doctor' or
                request.user.profile.user_type == 'agent'
        )

    def has_object_permission(self, request, view, obj):
        return request.user and (
                request.user.profile.user_type == 'doctor' or
                request.user.profile.user_type == 'agent'
        )


class IsAgentOrPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user and (
                request.user.profile.user_type == 'patient' or
                request.user.profile.user_type == 'agent'
        )

    def has_object_permission(self, request, view, obj):
        return request.user and (
                request.user.profile.user_type == 'patient' or
                request.user.profile.user_type == 'agent'
        )


class IsDoctorOrPatient(BasePermission):
    def has_permission(self, request, view):
        return request.user and (
                request.user.profile.user_type == 'patient' or
                request.user.profile.user_type == 'doctor'
        )

    def has_object_permission(self, request, view, obj):
        return request.user and (
                request.user.profile.user_type == 'patient' or
                request.user.profile.user_type == 'doctor'
        )
