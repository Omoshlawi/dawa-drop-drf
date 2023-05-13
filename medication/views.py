from django.shortcuts import render

from rest_framework import viewsets
from rest_framework import permissions
from core import permisions as custom_permissions
from .models import AppointMent, HIVLabTest, ARTRegimen, PatientHivMedication
from .serializers import (
    AppointMentSerializer, HIVLabTestSerializer,
    ARTRegimenSerializer, PatientHivMedicationSerializer
)


# Create your views here.


class AppointMentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrPatient
    ]
    serializer_class = AppointMentSerializer

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

    serializer_class = PatientHivMedicationSerializer

    def get_queryset(self):
        patient = self.request.user.patient
        queryset = patient.prescriptions.all()
        return queryset
