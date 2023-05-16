from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions
from core import permisions as custom_permissions
from .filterset import AppointMentFilterSet
from .models import AppointMent, HIVLabTest, ARTRegimen, PatientHivMedication
from .serializers import (
    AppointMentSerializer, HIVLabTestSerializer,
    ARTRegimenSerializer, PatientHivMedicationSerializer, PatientTriadSerializer
)


# Create your views here.


class AppointMentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrPatient
    ]
    serializer_class = AppointMentSerializer
    filterset_class = AppointMentFilterSet
    search_fields = (
        "doctor__user__first_name", "doctor__user__last_name",
        "doctor__user__profile__phone_number", "doctor__doctor_number"
    )

    def get_queryset(self):
        user = self.request.user
        if user.profile.user_type == 'doctor':
            queryset = user.doctor.appointments.all()
        else:
            queryset = user.patient.appointments.all()
        return queryset


class HIVLabTestViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
    ]
    queryset = HIVLabTest.objects.all()
    serializer_class = HIVLabTestSerializer


class PatientHIVLabTestViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient
    ]
    serializer_class = HIVLabTestSerializer

    def get_queryset(self):
        patient = self.request.user.patient
        queryset = HIVLabTest.objects.filter(appointment__patient=patient)
        return queryset


class ARTRegimenViewSet(viewsets.ModelViewSet):
    queryset = ARTRegimen.objects.all()
    serializer_class = ARTRegimenSerializer


class PatientHivMedicationViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient
    ]
    search_fields = (
        "doctor__user__first_name", "doctor__user__last_name",
        "doctor__user__profile__phone_number", "doctor__doctor_number",
        "regimen__regimen", "regimen__regimen_line"
    )
    serializer_class = PatientHivMedicationSerializer

    def get_queryset(self):
        patient = self.request.user.patient
        queryset = patient.prescriptions.all()
        return queryset


class PatientTriadViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]
    serializer_class = PatientTriadSerializer

    def get_queryset(self):
        return self.request.user.patient.triads.all()
