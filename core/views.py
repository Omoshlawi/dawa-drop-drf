from rest_framework import reverse
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import viewsets, permissions

from users.models import Patient
from . import permisions as custom_permissions
from .models import HealthFacility, DeliveryMode, FacilityTransferRequest, FacilityType, MaritalStatus, AppointMentType, \
    DeliveryTimeSlot
from .serializers import HealthFacilitySerializer, DeliveryModeSerializer, TransferRequestSerializer, \
    FacilityTypeSerializer, MaritalStatusSerializer, AppointMentTypeSerializer, DeliveryTimeSlotSerializer
from . import mixin


# Create your views here.


class ApiRootView(APIView):
    def get(self, request):
        return Response({
            "users_url": reverse.reverse_lazy('users:user-list', request=request),
            "doctors_url": reverse.reverse_lazy('doctors:doctor-list', request=request),
            # "doctors_url": reverse.reverse_lazy('users:user-doctor-list', request=request),
            "deliver_agents_url": reverse.reverse_lazy('agents:agent-list', request=request),
            "marital_status": reverse.reverse_lazy('core:marital-status-list', request=request),
            "appointment_types": reverse.reverse_lazy('core:appointment-types-list', request=request),
            "art_regimens": reverse.reverse_lazy('medication:regimen-list', request=request),
            "appointments": reverse.reverse_lazy('medication:appointment-list', request=request),
            # "deliver_agents_url": reverse.reverse_lazy('users:user-agent-list', request=request),
            "patients_url": reverse.reverse_lazy('patients:patient-list', request=request),
            "patients_transfer_request_url": reverse.reverse_lazy('core:transfer-request-list', request=request),
            "patients_lab_tests": reverse.reverse_lazy('medication:test-list', request=request),
            "patients_prescription": reverse.reverse_lazy('medication:patient-hiv-prescription-list', request=request),
            "enrollments_url": reverse.reverse_lazy('awards:enrollment-list', request=request),
            # "patients_url": reverse.reverse_lazy('users:user-patient-list', request=request),
            "health_facilities_types": reverse.reverse_lazy('core:facility-type-list', request=request),
            "health facilities url": reverse.reverse_lazy('core:facility-list', request=request),
            "award_programs_url": reverse.reverse_lazy('awards:program-list', request=request),
            "reward_url": reverse.reverse_lazy('awards:reward-list', request=request),
            "delivery_modes_url": reverse.reverse_lazy('core:mode-list', request=request),
            "orders_url": reverse.reverse_lazy('orders:order-list', request=request),
            "feedback_url": reverse.reverse_lazy('orders:feedback-list', request=request),
            "delivery_url": reverse.reverse_lazy('orders:delivery-request-list', request=request),
        })


class HealthFacilityViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny,
                          custom_permissions.IsDoctorOrReadOnly]
    queryset = HealthFacility.objects.all()
    serializer_class = HealthFacilitySerializer


class HealthFacilityTypeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.AllowAny,
        custom_permissions.IsDoctorOrReadOnly
    ]
    queryset = FacilityType.objects.all()
    serializer_class = FacilityTypeSerializer


class DeliveryModeViewSet(viewsets.ModelViewSet):
    permission_classes = [
        custom_permissions.IsAdminOrReadOnly
    ]
    queryset = DeliveryMode.objects.all()
    serializer_class = DeliveryModeSerializer


class TransferRequestViewSet(viewsets.ModelViewSet, mixin.PatientTransferMixin):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrReadOnly
    ]
    queryset = FacilityTransferRequest.objects.all()
    serializer_class = TransferRequestSerializer


class MaritalStatusViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrReadOnly
    ]
    queryset = MaritalStatus.objects.all()
    serializer_class = MaritalStatusSerializer


class AppointMentTypeViewSet(viewsets.ModelViewSet):
    queryset = AppointMentType.objects.all()
    serializer_class = AppointMentTypeSerializer


class DeliveryTimeSlotViewSet(viewsets.ModelViewSet):
    permission_classes = [
        custom_permissions.IsDoctorOrReadOnly
    ]
    queryset = DeliveryTimeSlot.objects.all()
    serializer_class = DeliveryTimeSlotSerializer
