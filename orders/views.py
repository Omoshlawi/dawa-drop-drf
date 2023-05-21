import secrets

from rest_framework import permissions, status
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response
from django.utils import timezone

from core.models import RefillScheme
from patients.api import get_prescriptions, get_remote_current_prescription
from patients.models import AppointMent
from users.utils import post_appointment_to_emr
from . import mixin
from core import permisions as custom_permissions
from users.models import Doctor, Patient
from .models import Order, Delivery, DeliveryFeedBack
from .serializers import OrderSerializer, DeliverySerializer, DeliveryFeedBackSerializer, DeliveryRequestSerializer, \
    DeliveryStartSerializer, AgentDeliverySerializer
from django.utils import timezone

from .utils import get_route_polyline


# Create your views here.

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType,
        custom_permissions.HasCurrentPrescriptionOrReadOnly
    ]

    def get_queryset(self):
        return Order.objects.filter(appointment__patient__user=self.request.user)

    def get_time_range(self):
        today = timezone.now().date()
        days = timezone.timedelta(days=1)
        tomorrow = today + days
        return today, tomorrow

    def perform_create(self, serializer):
        """
            Order creation steps
            1.Check if there exist an appointment with field next_appointment_date pointing to future or today
            2.If there exist such appointment,check if user is eligible to make an order based on the date
                i.e Maximum of 1 day earlier(Ordering today if tomorrow is next appointment date
            3.If ineligible:
                a.post data to emr to create new appointment similar to last one except for next appointment
                b.If created successfully, use response to create same appointment in dawadrop
            4.Create an order and link it to the new appontment appointment
        """
        patient = self.request.user.patient
        # 1.Get current patient due appointment of type refill where next date is
        # pointing to today or tomorrow
        appointments = patient.appointments.filter(
            next_appointment_date__range=self.get_time_range(),
            type__type='Refill'
        )
        # if none raise ineligible
        if not appointments.exists():
            raise PermissionDenied(
                detail="You are not eligible for making an Order, no appointment"
            )
        appointment = appointments.first()
        # Check if user is in any scheme
        refill_scheme = patient.refill_scheme
        default_schemes = RefillScheme.objects.filter(is_default=True)
        if not refill_scheme and default_schemes.exists():
            refill_scheme = default_schemes.first()

        next_appointment_date = None
        if refill_scheme:
            refill_delta = timezone.timedelta(**{refill_scheme.units: refill_scheme.time})
            next_appointment_date = appointment.next_appointment_date + refill_delta
            # Make sure no other refill appointment in the same date
            if patient.appointments.filter(
                    next_appointment_date=next_appointment_date,
                    type__type='Refill'
            ).exists():
                raise PermissionDenied(
                    detail="Order already made"
                )

        resp = post_appointment_to_emr({
            'previous_appointment': appointment.remote_id,
            'next_appointment_date': next_appointment_date
        })
        # Check if remote creation success
        # print("*******************************  ", resp.json())
        if resp.status_code != status.HTTP_201_CREATED:
            raise PermissionDenied(
                detail="Couldn't create to the server"
            )
        data = resp.json()
        new_appointment = self.create_appointment(data, appointment)

        serializer.save(appointment=new_appointment)

    def create_appointment(self, appointment_dict, curr_appointment):
        new_appointment = AppointMent.objects.create(
            remote_id=appointment_dict["id"],
            patient=curr_appointment.patient,
            type=curr_appointment.type,
            doctor=curr_appointment.doctor,
            next_appointment_date=appointment_dict["next_appointment_date"]
        )
        return new_appointment

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


class DeliveryRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DeliveryRequestSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsAgent,
        custom_permissions.HasRelatedUserType
    ]

    @action(detail=True, url_path='accept', url_name='accept', methods=['post'],
            serializer_class=DeliveryStartSerializer)
    def accept(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        random_string = secrets.token_hex(16)
        while Delivery.objects.filter(code=random_string).exists():
            random_string = secrets.token_hex(16)
        order = self.get_object()
        validated_data = serializer.validated_data
        start_indicator = True
        if validated_data.get("start", None) is not None:
            start_indicator = validated_data.pop("start")
        delivery = Delivery.objects.create(
            order=order,
            code=random_string,
            prescription=self.get_remote_current_prescription_id(),
            delivery_agent=self.request.user.agent,
            status='in_progress' if start_indicator else None,
            time_started=timezone.now() if start_indicator else None,
            **validated_data
        )
        serializer = AgentDeliverySerializer(instance=delivery, context={'request': request})
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def get_queryset(self):
        return Order.objects.filter(delivery__isnull=True)

    def get_remote_current_prescription_id(self):
        order = self.get_object()
        current = get_remote_current_prescription(order.appointment.patient)
        if current:
            return current["id"]
        return None


class DeliveriesViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AgentDeliverySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsAgent,
        custom_permissions.HasRelatedUserType,
    ]
    filterset_fields = {
        'status': ['isnull', 'exact'],
    }

    def get_queryset(self):
        if self.request.user.profile.user_type == 'agent':
            return self.request.user.agent.deliveries.all()
        Delivery.objects.all()

    @action(detail=True, url_path='start', url_name='start', methods=['post'],
            serializer_class=DeliveryStartSerializer)
    def start(self, request, *args, **kwargs):
        delivery = self.get_object()
        if delivery.status != 'in_progress':
            serializer = self.get_serializer(instance=delivery, data=request.data)
            serializer.is_valid(raise_exception=True)
            delivery = serializer.save(status='in_progress', time_started=timezone.now())
        return Response(data=DeliverySerializer(instance=delivery, context={'request': request}).data)

    @action(detail=True, url_path='cancel', url_name='cancel', methods=['get'])
    def cancel(self, request, *args, **kwargs):
        delivery = self.get_object()
        if delivery.status == 'in_progress':
            delivery.status = 'canceled'
            delivery.save()
        return Response(data={'detail': "Delivery canceled successfully"}, status=status.HTTP_200_OK)

    @action(
        detail=True, url_path='route', url_name='route', methods=['get'],
        queryset=Delivery.objects.all(),
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permissions.HasRelatedUserType,
        ])
    def route(self, request, *args, **kwargs):
        delivery = get_object_or_404(Delivery, **kwargs)
        if delivery.status == 'in_progress':
            geojson = get_route_polyline(
                {'latitude': delivery.latitude, 'longitude': delivery.longitude},
                {'latitude': delivery.order.latitude, 'longitude': delivery.order.longitude}
            )
            return Response(data=geojson)
        return Response(
            status=status.HTTP_400_BAD_REQUEST,
            data={'detail': 'You must start the delivery to get the route'}
        )


class DeliveryFeedBackViewSet(viewsets.ModelViewSet):
    serializer_class = DeliveryFeedBackSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        custom_permissions.IsPatient,
        custom_permissions.HasRelatedUserType
    ]

    def get_queryset(self):
        return DeliveryFeedBack.objects.filter(delivery__order__appointment__patient__user=self.request.user)
