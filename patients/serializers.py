from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse
from awards.serializers import PatientProgramEnrollmentSerializer, RedemptionSerializer
from core.models import HealthFacility, FacilityType, MaritalStatus, AppointMentType
from core.serializers import HealthFacilitySerializer, MaritalStatusSerializer, AppointMentTypeSerializer
from doctors.models import Doctor
from patients.mixin import PatientAppointmentSyncMixin, FacilitySyncMixin
from patients.models import PatientNextOfKeen, Patient, AppointMent


class PatientNextOfKeenSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return reverse(
            viewname='patients:next-of-keen-detail',
            args=[instance.patient.id, instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = PatientNextOfKeen
        fields = ('url', 'full_name', 'address', 'phone_number', 'created_at', 'updated_at')
        extra_kwargs = {
            'url': {'view_name': 'patients:next-of-keen-detail'},
        }


class PatientSerializer(serializers.HyperlinkedModelSerializer):
    base_clinic = serializers.HyperlinkedRelatedField(
        view_name='core:facility-detail', queryset=HealthFacility.objects.all()
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
                viewname='patients:patient-points',
                request=self.context.get('request'),
                args=[instance.id]
            ),
            'current_program_enrolment': PatientProgramEnrollmentSerializer(
                instance=instance.current_program_enrollment,
                context=self.context
            ).data if instance.current_program_enrollment is not None else None,
            'redeem_url': reverse(
                viewname='patients:patient-redeem-points',
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
                    viewname='patients:next-of-keen-list',
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

        marital_status = _dict.pop("marital_status")
        marital_status_obj = {
            'marital_status': MaritalStatusSerializer(
                instance=instance.marital_status,
                context=self.context
            ).data if instance.marital_status else None
        }

        _dict.update(marital_status_obj)
        _dict.update(nok_obj)
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Patient
        fields = (
            'url',
            'patient_number',
            'next_of_keen',
            'base_clinic',
            'county_of_residence',
            'enrollments',
            'marital_status',
            'loyalty_points',
            'created_at',
            'updated_at',
        )
        extra_kwargs = {
            'url': {'view_name': 'patients:patient-detail'},
            'patient_number': {'read_only': True},
            'marital_status': {'view_name': 'core:marital-status-detail'}
            # 'base_clinic': {'view_name': 'core:facility-detail'}
        }


class AppointMentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = AppointMent
        fields = (
            'url', 'id', 'patient', 'type', 'doctor', 'next_appointment_date',
            'created_at', 'updated_at'
        )
        extra_kwargs = {
            'url': {'view_name': 'patients:appointment-detail'},
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


class PatientAddUpdateSerializer(serializers.ModelSerializer, PatientAppointmentSyncMixin, FacilitySyncMixin):
    marital_status = serializers.JSONField()
    base_clinic = serializers.JSONField()
    prescriptions = serializers.JSONField()
    appointments = serializers.JSONField()
    next_of_keen = serializers.JSONField()

    class Meta:
        model = Patient
        fields = (
            'patient_number', 'date_of_birth', 'county_of_residence', 'occupation',
            'national_id', 'marital_status', 'base_clinic', 'next_of_keen',
            'prescriptions', 'appointments'
        )

    def update(self, instance, validated_data):
        facility = self.get_or_create_facility(validated_data.pop("base_clinic"))
        marital_status = self.get_or_create_marital_status(validated_data.pop("marital_status"))
        next_of_keen = validated_data.pop("next_of_keen")
        prescriptions = validated_data.pop('prescriptions')
        appointments = validated_data.pop('appointments')
        validated_data.update({'base_clinic': facility, 'marital_status': marital_status})
        updated_instance = super().update(instance, validated_data)
        self.update_or_create_nok(next_of_keen, updated_instance)
        self.update_or_create_appointments(appointments, updated_instance)
        return updated_instance

    def get_or_create_marital_status(self, marital_status_dict):
        marital_status = None
        try:
            marital_status = MaritalStatus.objects.get(remote_id=marital_status_dict["id"])
            # TODO update marital status type
        except MaritalStatus.DoesNotExist:
            marital_status = MaritalStatus.objects.create(
                remote_id=marital_status_dict["id"],
                status=marital_status_dict["status"],
                description=marital_status_dict["description"],
                is_active=marital_status_dict["is_active"]
            )
        return marital_status

    def update_or_create_nok(self, nok_dict, patient_instance):
        if nok_dict["count"] == 0:
            return
        for nok in nok_dict["list"]:
            try:
                PatientNextOfKeen.objects.get(remote_id=nok["id"])
                # TODO perfome update
            except PatientNextOfKeen.DoesNotExist:
                # create
                PatientNextOfKeen.objects.create(
                    remote_id=nok["id"],
                    patient=patient_instance,
                    full_name=nok["full_name"],
                    relationship=nok["relationship"],
                    address=nok["address"],
                    phone_number=nok["phone_number"]
                )
