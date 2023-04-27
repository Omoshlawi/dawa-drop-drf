import secrets

from rest_framework import permissions
from rest_framework import viewsets

from core import permisions as custom_permissions
from users.models import Doctor
from .models import Order, Delivery, DeliveryFeedBack
from .serializers import OrderSerializer, DeliverySerializer, DeliveryFeedBackSerializer


# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
    ]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


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
        serializer.save(code=random_string,doctor=doctor)


class DeliveryFeedBackViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryFeedBackSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient
    ]

    def get_queryset(self):
        return DeliveryFeedBack.objects.filter(delivery__order__user=self.request.user)
