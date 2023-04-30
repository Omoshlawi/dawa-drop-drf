from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions

from awards.models import LoyaltyProgram, Reward
from awards.serializers import LoyaltyProgramSerializer, RewardSerializer
from core import permisions as custom_permissions


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
