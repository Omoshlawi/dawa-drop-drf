from rest_framework import serializers

from core.models import HIVClinic, DeliveryMode, TransferRequest


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


class TransferRequestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransferRequest
        fields = (
            'url', 'patient', 'hospital', 'reason',
            'is_approved', 'approved_by', 'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'core:transfer-request-detail'},
            'patient': {'view_name': 'users:patient-detail'},
            'approved_by': {'view_name': 'users:doctor-detail'},
            'hospital': {'view_name': 'core:clinic-detail'},
        }


class PatientOnlyTransferSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TransferRequest
        fields = (
            'url', 'patient', 'hospital', 'reason',
            'is_approved', 'approved_by', 'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'core:transfer-request-detail'},
            'patient': {'view_name': 'users:patient-detail', 'read_only': True},
            'approved_by': {'view_name': 'users:doctor-detail', 'read_only': True},
            'is_approved': {'read_only': True},
            'hospital': {'view_name': 'core:clinic-detail'},
        }
