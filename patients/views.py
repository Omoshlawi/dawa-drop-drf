from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from core import permisions as custom_permissions
from patients import mixin
from patients.api import get_and_sync_appointments, get_prescriptions, get_triads, get_tests, \
    get_patient_summary_statistics
from patients.filterset import AppointMentFilterSet
from patients.models import Patient, PatientNextOfKeen
from patients.serializers import PatientSerializer, PatientNextOfKeenSerializer, AppointMentSerializer


# Create your views here.

class PatientViewSet(viewsets.ModelViewSet, mixin.LoyaltyPointsMixin):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientNextOfKeenViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatientOrReadOnly,
        custom_permissions.IsDoctorOrPatient,
        custom_permissions.HasRelatedUserType
    ]
    serializer_class = PatientNextOfKeenSerializer

    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, id=self.kwargs['patient_pk'], user=self.request.user)
        serializer.save(patient=patient)

    def get_queryset(self):
        if self.request.user.profile.user_type == 'doctor':
            return PatientNextOfKeen.objects.all()
        curr_patient = self.request.user.patient
        patient = get_object_or_404(Patient, id=self.kwargs['patient_pk'])
        if curr_patient != patient:
            raise PermissionDenied(
                detail="Warning!!Your are forbidden from accessing other patient private information",
            )
        return PatientNextOfKeen.objects.filter(patient=patient)


class AppointMentViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]
    serializer_class = AppointMentSerializer
    filterset_class = AppointMentFilterSet

    search_fields = (
        "doctor__user__first_name", "doctor__user__last_name",
        "doctor__user__profile__phone_number", "doctor__doctor_number"
    )

    def sync_with_emr(self, request):
        patient = request.user.patient
        get_and_sync_appointments(patient)

    def list(self, request, *args, **kwargs):
        self.sync_with_emr(request)
        return super().list(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.patient.appointments.all()


class MedicationViewSet(viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]

    def list(self, request, *args, **kwargs):
        return Response(
            data=get_prescriptions(self.request.user.patient)
        )


class PatientTriadViewSet(viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]

    def list(self, request, *args, **kwargs):
        return Response(data=get_triads(self.request.user.patient))


class PatientTestViewSet(viewsets.GenericViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]

    def list(self, request, *args, **kwargs):
        return Response(data=get_tests(self.request.user.patient))


class PatientSummaryViewSet(viewsets.ViewSet):
    def list(self, request):
        return Response(data=get_patient_summary_statistics())
