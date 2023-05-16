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


class HasRelatedUserType(BasePermission):
    message = "You do not have permission to perform this action, create your profile first."

    def has_permission(self, request, view):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.profile.has_related_user_type
        )

    def has_object_permission(self, request, view, obj):
        return (
                request.user and
                request.user.is_authenticated and
                request.user.profile.has_related_user_type
        )


class HasNoRelatedUserType(HasRelatedUserType):
    message = "You do not have permission to perform this action, your profile is already up to date."

    def has_permission(self, request, view):
        return not super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        return not super().has_object_permission(request, view, obj)


class HasCurrentPrescription(IsPatient):
    message = "You do not have permission to perform this action, you must have prescription,contact doctor for more."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.patient.current_prescription

    def has_object_permission(self, request, view, obj):
        super().has_object_permission(request, view, obj) and request.user.patient.current_prescription


class HasCurrentPrescriptionOrReadOnly(HasCurrentPrescription):

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return super().has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        super().has_object_permission(request, view, obj)


class HasCurrentEnrolledProgram(IsPatient):
    message = "You do not have permission to perform this action, you must be enrolled in loyalty programme."

    def has_permission(self, request, view):
        return super().has_permission(request, view) and request.user.patient.current_program_enrollment

    def has_object_permission(self, request, view, obj):
        super().has_object_permission(request, view, obj) and request.user.patient.current_program_enrollment
