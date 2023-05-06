from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import Http404
from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED
from rest_framework import permissions
from core import permisions as custom_permissions
from . import mixin
from users.serializers import (
    UserSerializer, UserCredentialSerializer,
    UserRegistrationSerializer, UserLoginSerializer,
    UserProfileSerializer, DoctorSerializer, PatientSerializer, DeliverAgentSerializer, PatientNextOfKeenSerializer,
    RedemptionSerializer
)
from .models import Doctor, Patient, DeliverAgent, PatientNextOfKeen
from rest_framework.exceptions import PermissionDenied


class UserViewSet(
    viewsets.ModelViewSet,
    mixin.DoctorsMixin,
    mixin.PatientsMixin,
    mixin.AgentsMixin,
    mixin.AuthMixin,
    mixin.ProfileMixin,
):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [
        permissions.IsAuthenticated
    ]

    @action(
        methods=['get'],
        detail=False,
        authentication_classes=[TokenAuthentication],
        permission_classes=[
            IsAuthenticated
        ],
        description="Get user by token",
        url_path='get-user-by-token'
    )
    def get_user_by_token(self, request, *args, **kwargs):
        user = request.user
        return Response(self.get_serializer(instance=user).data)


class DoctorsViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer


class PatientViewSet(viewsets.ModelViewSet, mixin.LoyaltyPointsMixin):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


class DeliverAgentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DeliverAgent.objects.all()
    serializer_class = DeliverAgentSerializer


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
