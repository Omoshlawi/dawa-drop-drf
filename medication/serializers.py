from rest_framework import serializers

from patients.models import Triad
from .models import AppointMent, HIVLabTest, ARTRegimen, PatientHivMedication
from core.serializers import AppointMentTypeSerializer


class HIVLabTestSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = HIVLabTest
        fields = ('url', 'id', 'appointment', 'cd4_count', 'viral_load')
        extra_kwargs = {
            'url': {'view_name': 'medication:test-detail'},
            'appointment': {'view_name': 'medication:appointment-detail'},
        }


class AppointMentSerializer(serializers.HyperlinkedModelSerializer):
    tests = HIVLabTestSerializer(many=True, read_only=True)

    class Meta:
        model = AppointMent
        fields = (
            'url', 'id', 'patient', 'type', 'doctor', 'tests', 'next_appointment_date',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'medication:appointment-detail'},
            'patient': {'view_name': 'patients:patient-detail'},
            'type': {'view_name': 'core:appointment-types-detail'},
            'doctor': {'view_name': 'doctors:doctor-detail'},
        }

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        from users.serializers import PublicProfileSerializer
        _dict.update({
            'doctor': PublicProfileSerializer(instance=instance.doctor.user.profile, context=self.context).data,
            'type': AppointMentTypeSerializer(instance=instance.type, context=self.context).data
        })
        return _dict


class ARTRegimenSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ARTRegimen
        fields = ('url', 'id', 'regimen_line', 'regimen', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'medication:regimen-detail'}
        }


class PatientHivMedicationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PatientHivMedication
        fields = ('url', 'id', 'patient', 'regimen', 'doctor', 'is_current', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'medication:patient-hiv-prescription-detail'},
            'patient': {'view_name': 'patients:patient-detail'},
            'regimen': {'view_name': 'medication:regimen-detail'},
            'doctor': {'view_name': 'doctors:doctor-detail'},
        }

    def to_representation(self, instance):
        from users.serializers import PublicProfileSerializer
        _dict = super().to_representation(instance)
        _dict.update({
            'doctor': PublicProfileSerializer(instance=instance.doctor.user.profile, context=self.context).data,
            'regimen': ARTRegimenSerializer(
                instance=instance.regimen,
                context=self.context
            ).data if instance.regimen else None
        })
        return _dict


class PatientTriadSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Triad
        fields = ('url', 'weight', 'height', 'temperature', 'heart_rate', 'blood_pressure', 'created_at')
        extra_kwargs = {
            'url': {'view_name': 'medication:triad-detail'}
        }

