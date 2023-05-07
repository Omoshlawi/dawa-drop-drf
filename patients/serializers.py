from rest_framework import serializers
from rest_framework.reverse import reverse

from awards.serializers import PatientProgramEnrollmentSerializer, RedemptionSerializer
from core.models import HealthFacility
from core.serializers import HealthFacilitySerializer
from patients.models import PatientNextOfKeen, Patient


class PatientNextOfKeenSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return reverse(
            viewname='users:next-of-keen-detail',
            args=[instance.patient.id, instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = PatientNextOfKeen
        fields = ('url', 'full_name', 'address', 'phone_number', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'users:next-of-keen-detail'},
        }


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    base_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:clinic-detail', queryset=HealthFacility.objects.all()
    )
    next_of_keen = PatientNextOfKeenSerializer(many=True, read_only=True)
    loyalty_points = serializers.SerializerMethodField()
    enrollments = PatientProgramEnrollmentSerializer(many=True, read_only=True)

    # redemptions = serializers.SerializerMethodField()

    def get_loyalty_points(self, instance):
        return {
            'total': instance.total_points,
            'total_redeemed_points': instance.total_redemption_points,
            'redeem_count': instance.redemptions.all().count(),
            'redeemable_points': instance.points_balance,
            'points_url': reverse(
                viewname='users:patient-points',
                request=self.context.get('request'),
                args=[instance.id]
            ),
            'current_program_enrolment': PatientProgramEnrollmentSerializer(
                instance=instance.current_program_enrollment,
                context=self.context
            ).data if instance.current_program_enrollment is not None else None,
            'redeem_url': reverse(
                viewname='users:patient-redeem-points',
                request=self.context.get('request'),
                args=[instance.id]
            ),
            'redeem_list': RedemptionSerializer(
                instance=instance.redemptions,
                many=True,
                context=self.context
            ).data
        }

    def to_representation(self, instance):
        _dict = super().to_representation(instance)
        nok = _dict.pop("next_of_keen")
        nok_obj = {
            'next_of_keen': {
                'count': len(nok),
                'url': reverse(
                    viewname='users:next-of-keen-list',
                    args=[instance.id],
                    request=self.context.get('request')
                ),
                'list': nok
            }
        }
        base_clinic_url = _dict.pop("base_clinic")
        base_clinic_obj = {
            'base_clinic': HealthFacilitySerializer(
                instance=instance.base_clinic,
                context=self.context
            ).data
        }
        _dict.update(nok_obj)
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Patient
        fields = (
            'url',
            'patient_number', 'next_of_keen',
            'base_clinic',
            # 'redemptions',
            'enrollments',
            'loyalty_points',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'users:patient-detail'},
            'patient_number': {'read_only': True},
            # 'base_clinic': {'view_name': 'core:clinic-detail'}
        }
