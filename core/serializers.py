from rest_framework import serializers

from core.models import HIVClinic, DeliveryMode


class HIVClinicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HIVClinic
        fields = ('url', 'name', 'longitude', 'latitude', 'address')
        extra_kwargs = {
            'url': {'view_name': 'core:clinic-detail'}
        }


class DeliveryModeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryMode
        fields = ('url', 'mode',)
        extra_kwargs = {
            'url': {'view_name': 'core:mode-detail'}
        }
