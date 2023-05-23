from django.core.handlers.asgi import ASGIRequest
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from agents.models import DeliverAgent
from awards.models import LoyaltyProgram
from patients.models import Patient
from users.serializers import PublicProfileSerializer
from .models import Order, Delivery, DeliveryFeedBack
from core.serializers import DeliveryModeSerializer, DeliveryTimeSlotSerializer


class DeliveryRequestSerializer(serializers.ModelSerializer):
    delivery_mode = DeliveryModeSerializer(read_only=True)
    time_slot = DeliveryTimeSlotSerializer(read_only=True)
    accept_url = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()

    def get_destination(self, instance):
        return {'latitude': instance.latitude, 'longitude': instance.longitude}

    def get_accept_url(self, instance):
        return reverse(
            'orders:delivery-request-accept',
            args=[instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = Order
        fields = (
            'destination', 'address', 'accept_url',
            'delivery_mode', 'time_slot', 'created_at'
        )


class DeliveryStartSerializer(serializers.Serializer):
    def update(self, instance, validated_data):
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def create(self, validated_data):
        pass

    longitude = serializers.DecimalField(max_digits=22, decimal_places=16, required=True)
    latitude = serializers.DecimalField(max_digits=22, decimal_places=16, required=True)
    start = serializers.BooleanField(required=False, default=True)


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    """
    Only allows undelivered goods delivery
    """
    delivery_id = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    start_location = serializers.SerializerMethodField()
    start_url = serializers.SerializerMethodField()
    cancel_url = serializers.SerializerMethodField()
    route_url = serializers.SerializerMethodField()
    location_stream_url = serializers.SerializerMethodField()
    prescription = serializers.SerializerMethodField()

    def get_prescription(self, instance):
        return list(
            filter(
                lambda pres: pres["id"] == instance.prescription,
                instance.order.appointment.patient.prescriptions
            )
        )[0]

    def get_start_url(self, instance):
        return reverse(
            'orders:delivery-start', args=[instance.id],
            request=self.context.get('request')
        )

    def get_location_stream_url(self, instance):
        request: ASGIRequest = self.context.get('request')
        return f"ws://{request.get_host()}/ws/delivery/{instance.id}/"

    def get_cancel_url(self, instance):
        return reverse(
            'orders:delivery-cancel', args=[instance.id],
            request=self.context.get('request')
        )

    def get_route_url(self, instance):
        return reverse(
            'orders:delivery-route', args=[instance.id],
            request=self.context.get('request')
        )

    def get_destination(self, instance):
        return {'latitude': instance.order.latitude, 'longitude': instance.order.longitude}

    def get_start_location(self, instance):
        return {'latitude': instance.latitude, 'longitude': instance.longitude}

    def get_delivery_id(self, instance):
        return instance.get_id()

    def get_agent(self, instance):
        return PublicProfileSerializer(
            instance=instance.delivery_agent.user.profile,
            context=self.context
        ).data

    def get_doctor(self, instance):
        return PublicProfileSerializer(
            instance=instance.order.appointment.doctor.user.profile,
            context=self.context
        ).data

    class Meta:
        model = Delivery
        fields = [
            'url', 'delivery_id', 'order', 'prescription', 'destination', 'start_location',
            'start_url', 'cancel_url', 'time_started', 'route_url', 'status', 'location_stream_url',
            # 'code',
            'created_at', 'agent', 'doctor'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:delivery-request-detail'},
            'order': {'view_name': 'orders:order-detail', 'queryset': Order.objects.filter(delivery__isnull=True)},
            # 'code': {'read_only': True},
        }


class AgentDeliverySerializer(serializers.HyperlinkedModelSerializer):
    """

    """
    delivery_id = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    start_location = serializers.SerializerMethodField()
    start_url = serializers.SerializerMethodField()
    cancel_url = serializers.SerializerMethodField()
    route_url = serializers.SerializerMethodField()
    location_stream_url = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_status(self, instance):
        if instance.order.is_delivered:
            return 'delivered'
        return instance.status

    def get_address(self, instance):
        return instance.order.address

    def get_phone_number(self, instance):
        phone = None
        if instance.order.reach_out_phone_number:
            phone = instance.order.reach_out_phone_number
        else:
            phone = instance.order.appointment.patient.user.profile.phone_number
        return str(phone) if phone else None

    def get_start_url(self, instance):
        return reverse(
            'orders:delivery-start', args=[instance.id],
            request=self.context.get('request')
        )

    def get_location_stream_url(self, instance):
        request: ASGIRequest = self.context.get('request')
        return f"ws://{request.get_host()}/ws/delivery/{instance.id}/"

    def get_cancel_url(self, instance):
        return reverse(
            'orders:delivery-cancel', args=[instance.id],
            request=self.context.get('request')
        )

    def get_route_url(self, instance):
        return reverse(
            'orders:delivery-route', args=[instance.id],
            request=self.context.get('request')
        )

    def get_destination(self, instance):
        return {'latitude': instance.order.latitude, 'longitude': instance.order.longitude}

    def get_start_location(self, instance):
        return {'latitude': instance.latitude, 'longitude': instance.longitude}

    def get_delivery_id(self, instance):
        return instance.get_id()

    def get_agent(self, instance):
        return PublicProfileSerializer(
            instance=instance.delivery_agent.user.profile,
            context=self.context
        ).data

    def get_doctor(self, instance):
        return PublicProfileSerializer(
            instance=instance.order.appointment.doctor.user.profile,
            context=self.context
        ).data

    class Meta:
        model = Delivery
        fields = [
            'url', 'delivery_id', 'order', 'prescription', 'destination', 'start_location',
            'start_url', 'cancel_url', 'time_started', 'route_url', 'status', 'location_stream_url',
            # 'code',
            'created_at', 'agent', 'doctor', 'phone_number', 'address'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:delivery-request-detail'},
            'order': {'view_name': 'orders:order-detail', 'queryset': Order.objects.filter(delivery__isnull=True)},
            # 'code': {'read_only': True},
        }


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    order_id = serializers.SerializerMethodField()
    is_delivered = serializers.SerializerMethodField()
    is_allocated = serializers.SerializerMethodField()
    delivery = DeliverySerializer(read_only=True)

    def get_order_id(self, instance):
        return instance.get_id()

    def get_is_delivered(self, instance):
        return instance.is_delivered

    def get_is_allocated(self, instance):
        return instance.is_allocated

    class Meta:
        model = Order
        fields = [
            'url', 'order_id', 'delivery_mode', 'time_slot',  # 'appointment',
            'reach_out_phone_number', 'longitude', 'latitude',
            'address', 'is_delivered', 'is_allocated', 'delivery', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:order-detail', 'read_only': True},
            'delivery': {'view_name': 'orders:delivery-request-detail', 'read_only': True},
            'delivery_mode': {'view_name': 'core:mode-detail'},
            'time_slot': {'view_name': 'core:time-slot-detail'},
        }

    def to_representation(self, instance):
        from core.serializers import DeliveryModeSerializer, DeliveryTimeSlotSerializer
        _dict = super().to_representation(instance)
        _dict.update({
            'delivery_mode': DeliveryModeSerializer(
                instance=instance.delivery_mode, context=self.context
            ).data if instance.delivery_mode else None,
            'time_slot': DeliveryTimeSlotSerializer(
                instance=instance.time_slot, context=self.context
            ).data if instance.time_slot else None,
            # 'appointment': AppointMentSerializer(
            #     instance=instance.appointment, context=self.context
            # ).data if instance.appointment else None
        })
        return _dict


class DeliveryFeedBackSerializer(serializers.HyperlinkedModelSerializer):
    code = serializers.CharField(max_length=32, write_only=True)
    order = serializers.SerializerMethodField()

    def get_order(self, instance):
        return reverse('orders:order-detail', args=[instance.delivery.order.id], request=self.context.get('request'))

    class Meta:
        model = DeliveryFeedBack
        fields = ['url', 'code', 'order', 'review', 'rating', 'created_at']
        extra_kwargs = {
            'url': {'view_name': 'orders:feedback-detail'},
        }

    def validate_code(self, attr):
        try:
            delivery = Delivery.objects.get(
                code=attr,
                order__appointment__patient__user=self.context.get(
                    'request').user
            )
            if DeliveryFeedBack.objects.filter(delivery=delivery).exists():
                raise ValidationError("Invalid Code, the code has been used")
            return attr
        except Delivery.DoesNotExist:
            raise ValidationError(
                "Invalid code, please scan again or type manually")

    def create(self, validated_data):
        user = self.context.get('request').user
        patient = user.patient
        enrollment = patient.current_program_enrollment
        if enrollment is not None:
            validated_data.update(
                {'points_awarded': enrollment.program.unit_point})
        code = validated_data.pop('code')
        delivery = Delivery.objects.get(code=code)
        validated_data.update({'delivery': delivery})
        return super().create(validated_data)
