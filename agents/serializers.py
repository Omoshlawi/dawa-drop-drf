from rest_framework import serializers

from agents.models import DeliverAgent
from core.serializers import HealthFacilitySerializer


class DeliverAgentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliverAgent
        fields = ('url', 'agent_number', 'delivery_mode',
                  'work_clinic',
                  'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'agents:agent-detail'},
            'agent_number': {'read_only': True},
            'delivery_mode': {'view_name': 'core:mode-detail'},
            'work_clinic': {'view_name': 'core:facility-detail'}
        }

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        base_clinic_url = _dict.pop("work_clinic")
        base_clinic_obj = {
            'work_clinic': HealthFacilitySerializer(
                instance=instance.work_clinic,
                context=self.context
            ).data
        }
        _dict.update(base_clinic_obj)
        return _dict

