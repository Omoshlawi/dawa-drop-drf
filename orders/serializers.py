from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.reverse import reverse

from .models import Order, Delivery, DeliveryFeedBack


class OrderSerializer(serializers.HyperlinkedModelSerializer):
    order_id = serializers.SerializerMethodField()
    is_delivered = serializers.SerializerMethodField()
    is_approved = serializers.SerializerMethodField()

    def get_order_id(self, instance):
        return instance.get_id()

    def get_is_delivered(self, instance):
        return instance.is_delivered

    def get_is_approved(self, instance):
        return instance.is_approved

    class Meta:
        model = Order
        fields = [
            'url', 'order_id', 'user', 'national_id', 'date_of_depletion',
            'reach_out_phone_number', 'longitude', 'latitude',
            'address', 'is_delivered', 'is_approved', 'created_at', 'updated_at'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:order-detail', 'read_only': True},
            'user': {'view_name': 'users:user-detail', 'read_only': True}
        }


class DeliverySerializer(serializers.HyperlinkedModelSerializer):
    """
    Only allows undelivered goods delivery
    """

    class Meta:
        model = Delivery
        fields = [
            'url', 'order', 'code', 'created_at',
            'delivery_medicine', 'instruction',
            'delivery_agent'
        ]
        extra_kwargs = {
            'url': {'view_name': 'orders:delivery-detail'},
            'order': {'view_name': 'orders:order-detail', 'queryset': Order.objects.filter(delivery__isnull=True)},
            'code': {'read_only': True},
            'delivery_agent': {'view_name': 'users:agent-detail'},
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
            delivery = Delivery.objects.get(code=attr, order__user=self.context.get('request').user)
            if DeliveryFeedBack.objects.filter(delivery=delivery):
                raise ValidationError("Invalid Code, the code has been used")
            return attr
        except Delivery.DoesNotExist:
            raise ValidationError("Invalid code, please scan again or type manually")

    def create(self, validated_data):
        code = validated_data.pop('code')
        delivery = Delivery.objects.get(code=code)
        validated_data.update({'delivery': delivery})
        return super().create(validated_data)
