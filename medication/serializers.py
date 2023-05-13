from rest_framework import serializers

from .models import AppointMent, HIVLabTest, ARTRegimen, PatientHivMedication


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
            'url': {'view_name': 'appointment-detail'},
            'patient': {'view_name': 'patients:patient-detail'},
            'type': {'view_name': 'core:appointment-types-detail'},
            'doctor': {'view_name': 'doctors:doctor-detail'},
        }


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
        _dict = super().to_representation(instance)
        regimen = _dict.pop("regimen")
        regimen_obje = {
            'regimen': ARTRegimenSerializer(
                instance=instance.regimen,
                context=self.context
            ).data if instance.regimen else None
        }
        _dict.update(regimen_obje)
        return _dict
