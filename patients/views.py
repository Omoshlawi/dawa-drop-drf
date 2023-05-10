from django.shortcuts import render
from rest_framework import viewsets, permissions
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import get_object_or_404

from core import permisions as custom_permissions
from patients import mixin
from patients.models import Patient, PatientNextOfKeen, Triad
from patients.serializers import PatientSerializer, PatientNextOfKeenSerializer, TriadSerializer


# Create your views here.

class PatientViewSet(viewsets.ModelViewSet, mixin.LoyaltyPointsMixin):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class PatientNextOfKeenViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatientOrReadOnly,
        custom_permissions.IsDoctorOrPatient
    ]
    serializer_class = PatientNextOfKeenSerializer

    def perform_create(self, serializer):
        patient = get_object_or_404(Patient, id=self.kwargs['patient_pk'], user=self.request.user)
        serializer.save(patient=patient)

    def get_queryset(self):
        if self.request.user.profile.user_type == 'doctor':
            return PatientNextOfKeen.objects.all()
        curr_patient = Patient.objects.get_or_create(
            user=self.request.user
        )[0]
        patient = get_object_or_404(Patient, id=self.kwargs['patient_pk'])
        if curr_patient != patient:
            raise PermissionDenied(
                detail="Warning!!Your are forbidden from accessing other patient private information",
            )
        return PatientNextOfKeen.objects.filter(patient=patient)


class TriadViewSet(viewsets.ModelViewSet):
    serializer_class = TriadSerializer
    permission_classes = [custom_permissions.IsDoctorOrReadOnly]

    def get_queryset(self):
        return Triad.objects.all()
