from rest_framework import serializers

from core.models import HealthFacility, DeliveryMode, FacilityTransferRequest, FacilityType, MaritalStatus, \
    AppointMentType, DeliveryTimeSlot


class HealthFacilitySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HealthFacility
        fields = ('url', 'identification_code', 'name', 'type', 'longitude', 'latitude', 'address')
        extra_kwargs = {
            'url': {'view_name': 'core:facility-detail'},
            'type': {'view_name': "core:facility-type-detail"}
        }


class FacilityTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = FacilityType
        fields = ('url', 'level', 'name', 'description')
        extra_kwargs = {
            'url': {'view_name': "core:facility-type-detail"}
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
            'hospital': {'view_name': 'core:facility-detail'},
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
            'hospital': {'view_name': 'core:facility-detail'},
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


class MaritalStatusSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MaritalStatus
        fields = ('url', 'status', 'description', 'is_active', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'core:marital-status-detail'}
        }


class AppointMentTypeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AppointMentType
        fields = ('url', 'id', 'code', 'type', 'description', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'core:appointment-types-detail'}
        }


class DeliveryTimeSlotSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryTimeSlot
        fields = ('url', 'slot', 'start', 'end', 'description')
        extra_kwargs = {
            'url': {'view_name': "core:time-slot-detail"}
        }
