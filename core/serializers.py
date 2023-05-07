from rest_framework import serializers

from core.models import HealthFacility, DeliveryMode, FacilityTransferRequest


class HealthFacilitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HealthFacility
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


class TransferRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FacilityTransferRequest
        fields = (
            'url', 'patient', 'hospital', 'reason',
            'is_approved', 'approved_by', 'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'core:transfer-request-detail'},
            'patient': {'view_name': 'patients:patient-detail'},
            'approved_by': {'view_name': 'doctors:doctor-detail'},
            'hospital': {'view_name': 'core:clinic-detail'},
        }


class PatientOnlyTransferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FacilityTransferRequest
        fields = (
            'url', 'patient', 'hospital', 'reason',
            'is_approved', 'approved_by', 'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'core:transfer-request-detail'},
            'patient': {'view_name': 'patients:patient-detail', 'read_only': True},
            'approved_by': {'view_name': 'doctors:doctor-detail', 'read_only': True},
            'is_approved': {'read_only': True},
            'hospital': {'view_name': 'core:clinic-detail'},
        }

    def to_representation(self, instance):
        from users.serializers import PublicProfileSerializer
        _dict = super().to_representation(instance=instance)
        hospital_url = _dict.pop('hospital')
        hospital_obj = {
            'hospital': HealthFacilitySerializer(instance=instance.hospital, context=self.context).data
        }
        approved_by_url = _dict.pop('approved_by')
        approved_by_obj = {
            'approved_by': PublicProfileSerializer(
                instance=instance.approved_by.user.profile,
                context=self.context
            ).data if instance.approved_by else None
        }
        _dict.update(hospital_obj)

        _dict.update(approved_by_obj)
        return _dict
