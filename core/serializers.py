from rest_framework import serializers

from core.models import HIVClinic


class HIVClinicSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HIVClinic
        fields = ('url', 'name', 'longitude', 'latitude', 'address')
        extra_kwargs = {
            'url': {'view_name': 'core:clinic-detail'}
        }
