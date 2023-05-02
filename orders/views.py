import secrets

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core import permisions as custom_permissions
from users.models import Doctor, Patient
from .models import Order, Delivery, DeliveryFeedBack, AgentTrip
from .serializers import OrderSerializer, DeliverySerializer, DeliveryFeedBackSerializer, AgentTripSerializer


# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
    ]

    def get_queryset(self):
        return Order.objects.filter(patient__user=self.request.user)

    def perform_create(self, serializer):
        patient = Patient.objects.get_or_create(user=self.request.user)[0]
        serializer.save(patient=patient)

    @action(detail=False, methods=['GET'])
    def pending(self, request, *args, **kwargs):
        """Fetch all the order with delivery object(approved) bt no delivered back (undelivered)"""
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter(delivery__isnull=False, delivery__feedback__isnull=True)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class DeliveryViewSet(viewsets.ModelViewSet):
    queryset = Delivery.objects.all()
    serializer_class = DeliverySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsDoctorOrReadOnly
    ]

    def perform_create(self, serializer):
        random_string = secrets.token_hex(16)
        # make sure its unique
        while Delivery.objects.filter(code=random_string):
            random_string = secrets.token_hex(16)
        # create delivery object
        doctor = Doctor.objects.get_or_create(user=self.request.user)[0]
        serializer.save(code=random_string, doctor=doctor)


class DeliveryFeedBackViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryFeedBackSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient
    ]

    def get_queryset(self):
        return DeliveryFeedBack.objects.filter(delivery__order__patient__user=self.request.user)


class AgentTripViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    queryset = AgentTrip.objects.all()
    serializer_class = AgentTripSerializer
