from rest_framework import serializers
from rest_framework.reverse import reverse

from core.models import HealthFacility
from core.serializers import HealthFacilitySerializer
from doctors.models import Doctor
from patients.models import PatientNextOfKeen


class DoctorSerializer(serializers.ModelSerializer):
    hiv_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:clinic-detail', queryset=HealthFacility.objects.all()
    )

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        base_clinic_url = _dict.pop("hiv_clinic")
        base_clinic_obj = {
            'hiv_clinic': HealthFacilitySerializer(
                instance=instance.hiv_clinic,
                context=self.context
            ).data
        }
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Doctor
        fields = (
            'url',
            'doctor_number',
            'hiv_clinic',
            'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'doctors:doctor-detail'},
            'doctor_number': {'read_only': True},
            # 'hiv_clinic': {'view_name': 'core:clinic-detail'}

        }


class DoctorNextOfKeenSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return reverse(
            viewname='patients:next-of-keen-detail',
            args=[instance.patient.id, instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = PatientNextOfKeen
        fields = ('url', 'patient', 'full_name', 'address', 'phone_number', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'patients:next-of-keen-detail'},
            'patient': {'view_name': 'patients:patient-detail'},
        }
