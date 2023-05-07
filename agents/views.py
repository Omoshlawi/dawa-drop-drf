from django.shortcuts import render
from rest_framework import viewsets, permissions

from agents.models import DeliverAgent
from agents.serializers import DeliverAgentSerializer


# Create your views here.

class DeliverAgentViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = DeliverAgent.objects.all()
    serializer_class = DeliverAgentSerializer
