from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from awards.models import LoyaltyProgram
from users.models import DeliverAgent, Patient, PatientProgramEnrollment
from users.serializers import PublicProfileSerializer
from .models import Order, Delivery, DeliveryFeedBack, AgentTrip


class AgentTripSerializer(serializers.HyperlinkedModelSerializer):
    current_location = serializers.SerializerMethodField()
    destination = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    trip_id = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    def get_status(self, instance):
        return instance.status

    def get_trip_id(self, instance):
        return instance.get_id()

    def get_agent(self, instance):
        return PublicProfileSerializer(
            instance=instance.delivery.delivery_agent.user.profile,
            context=self.context
        ).data

    def get_current_location(self, instance):
        return {
            "latitude": instance.latitude,
            "longitude": instance.longitude
        }

    def get_destination(self, instance):
        return {
            "latitude": instance.delivery.order.latitude,
            "longitude": instance.delivery.order.longitude
        }

    class Meta:
        model = AgentTrip
        fields = (
            'url', 'trip_id', 'delivery', 'status', 'current_location',
            'latitude', 'longitude',
            'destination', 'agent', 'created_at', 'updated_at'
        )
        extra_kwargs = {
            'delivery': {
                'view_name': 'orders:delivery-detail',
                'queryset': Delivery.objects.filter(feedback__isnull=True)
            },
            'url': {'view_name': 'orders:trip-detail'},
            'latitude': {'write_only': True},
            'longitude': {'write_only': True},
        }


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    """
    Only allows undelivered goods delivery
    """
    delivery_id = serializers.SerializerMethodField()
    doctor = serializers.SerializerMethodField()
    agent = serializers.SerializerMethodField()
    trip = AgentTripSerializer(read_only=True)

    def get_delivery_id(self, instance):
        return instance.get_id()

    def get_agent(self, instance):
        return PublicProfileSerializer(
            instance=instance.delivery_agent.user.profile,
            context=self.context
        ).data

    def get_doctor(self, instance):
        return PublicProfileSerializer(
            instance=instance.doctor.user.profile,
            context=self.context
        ).data

    class Meta:
        model = Delivery
        fields = [
            'url', 'delivery_id', 'order', 'trip',
            # 'code',
            'created_at', 'agent',
            'delivery_medicine', 'instruction',
            'delivery_agent', 'doctor'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:delivery-detail'},
            'order': {'view_name': 'orders:order-detail', 'queryset': Order.objects.filter(delivery__isnull=True)},
            # 'code': {'read_only': True},
            'delivery_agent': {
                'view_name': 'users:agent-detail',
                'write_only': True,
                'queryset': DeliverAgent.objects.filter(is_approved=True)
            },
        }


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    order_id = serializers.SerializerMethodField()
    is_delivered = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()
    delivery = DeliverySerializer(read_only=True)

    def get_order_id(self, instance):
        return instance.get_id()

    def get_is_delivered(self, instance):
        return instance.is_delivered

    def get_is_approved(self, instance):
        return instance.is_approved

    class Meta:
        model = Order
        fields = [
            'url', 'order_id', 'patient', 'national_id', 'date_of_depletion',
            'reach_out_phone_number', 'longitude', 'latitude',
            'address', 'is_delivered', 'is_approved', 'delivery', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:order-detail', 'read_only': True},
            'patient': {'view_name': 'users:patient-detail', 'read_only': True},
            'delivery': {'view_name': 'orders:delivery-detail', 'read_only': True},
        }


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
                order__patient__user=self.context.get('request').user
            )
            if DeliveryFeedBack.objects.filter(delivery=delivery).exists():
                raise ValidationError("Invalid Code, the code has been used")
            return attr
        except Delivery.DoesNotExist:
            raise ValidationError("Invalid code, please scan again or type manually")

    def create(self, validated_data):
        user = self.context.get('request').user
        patient = Patient.objects.get_or_create(user=user)[0]
        enrollment = patient.current_program_enrollment
        if enrollment is not None:
            validated_data.update({'points_awarded': enrollment.program.unit_point})
        code = validated_data.pop('code')
        delivery = Delivery.objects.get(code=code)
        validated_data.update({'delivery': delivery})
        return super().create(validated_data)
