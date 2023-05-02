from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.generics import get_object_or_404

from awards.models import LoyaltyProgram, Reward, PatientProgramEnrollment
from awards.serializers import LoyaltyProgramSerializer, RewardSerializer, RedemptionSerializer, \
    PatientProgramEnrollmentSerializer
from core import permisions as custom_permissions
from users.models import Patient


# Create your views here.


class LoyaltyProgramViewSet(viewsets.ModelViewSet):
    queryset = LoyaltyProgram.objects.all()
    serializer_class = LoyaltyProgramSerializer
    permission_classes = [
        custom_permissions.IsDoctorOrReadOnly
    ]


class RewardViewSet(viewsets.ModelViewSet):
    queryset = Reward.objects.all()
    serializer_class = RewardSerializer
    permission_classes = [
        custom_permissions.IsDoctorOrReadOnly
    ]


class PatientRedemptionViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient
    ]
    serializer_class = RedemptionSerializer

    # http_method_names = ['get', 'post']

    def get_queryset(self):
        return self.request.user.patient.redemptions.all()

    def perform_create(self, serializer):
        # todo can check if curr user in request is the one whose pk is there in kwargs
        points_redeemed = serializer.validated_data.get("reward").point_value
        patient = get_object_or_404(Patient, id=self.kwargs['patient_pk'])
        serializer.save(patient=patient, points_redeemed=points_redeemed)
        # todo make sure user is subscribed to program


class PatientProgramEnrollmentViewSet(viewsets.ModelViewSet):
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrReadOnly,
    ]
    serializer_class = PatientProgramEnrollmentSerializer
    queryset = PatientProgramEnrollment.objects.all()
