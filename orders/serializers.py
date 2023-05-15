from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from agents.models import DeliverAgent
from awards.models import LoyaltyProgram
from patients.models import Patient
from users.serializers import PublicProfileSerializer
from .models import Order, Delivery, DeliveryFeedBack
from medication.serializers import AppointMentSerializer, ARTRegimenSerializer
from core.serializers import DeliveryModeSerializer, DeliveryTimeSlotSerializer


class DeliveryRequestSerializer(serializers.ModelSerializer):
    delivery_mode = DeliveryModeSerializer(read_only=True)
    time_slot = DeliveryTimeSlotSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "longitude", 'latitude', 'address',
            'delivery_mode', 'time_slot', 'created_at'
        )


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    """
    Only allows undelivered goods delivery
    """
    delivery_id = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    prescription = ARTRegimenSerializer(read_only=True)

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
            'url', 'delivery_id', 'order', 'prescription',
            # 'code',
            'created_at', 'agent', 'doctor'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:delivery-request-detail'},
            # 'prescription': {'view_name': 'medication:regimen-detail'},
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
            # 'appointment': {'read_only': True, 'view_name': 'medication:appointment-detail'}
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
        patient = Patient.objects.get_or_create(user=user)[0]
        enrollment = patient.current_program_enrollment
        if enrollment is not None:
            validated_data.update(
                {'points_awarded': enrollment.program.unit_point})
        code = validated_data.pop('code')
        delivery = Delivery.objects.get(code=code)
        validated_data.update({'delivery': delivery})
        return super().create(validated_data)
