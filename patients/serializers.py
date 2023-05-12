from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_nested import serializers as nested_serializer
from awards.serializers import PatientProgramEnrollmentSerializer, RedemptionSerializer
from core.models import HealthFacility, FacilityType, MaritalStatus
from core.serializers import HealthFacilitySerializer, MaritalStatusSerializer, EmrMaritalStatusSerializer, \
    EmrHealthFacilitySerializer
from patients.models import PatientNextOfKeen, Patient, Triad


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
    triads = nested_serializer.NestedHyperlinkedIdentityField(
        many=True, view_name='patients:triad-detail',
        read_only=True, parent_lookup_kwargs={'patient_pk': 'patient__pk'}
    )

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
        triad_list = _dict.pop('triads')
        triads_obj = {
            'triads': {
                'count': len(triad_list),
                'url': reverse(
                    viewname='patients:triad-list',
                    args=[instance.id],
                    request=self.context.get('request')
                ),
                'url_list': triad_list
            }
        }
        marital_status = _dict.pop("marital_status")
        marital_status_obj = {
            'marital_status': MaritalStatusSerializer(
                instance=instance.marital_status,
                context=self.context
            ).data if instance.marital_status else None
        }
        _dict.update(marital_status_obj)
        _dict.update(triads_obj)
        _dict.update(nok_obj)
        _dict.update(base_clinic_obj)
        return _dict

    class Meta:
        model = Patient
        fields = (
            'url',
            'triads',
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


class TriadSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()

    def get_url(self, instance):
        return reverse(
            viewname='patients:triad-detail',
            args=[instance.patient.id, instance.id],
            request=self.context.get('request')
        )

    class Meta:
        model = Triad
        fields = (
            'url',
            'patient', 'weight', 'height',
            'temperature', 'heart_rate',
            'blood_pressure', 'created_at'
        )
        extra_kwargs = {
            'patient': {'view_name': 'patients:patient-detail', 'read_only': True},
        }


class PatientAddUpdateSerializer(serializers.ModelSerializer):
    marital_status = serializers.JSONField()
    base_clinic = serializers.JSONField()

    class Meta:
        model = Patient
        fields = (
            'patient_number', 'date_of_birth', 'county_of_residence', 'occupation',
            'national_id', 'marital_status', 'base_clinic'
        )

    def update(self, instance, validated_data):
        facility = self.get_or_create_facility(validated_data.pop("base_clinic"))
        marital_status = self.get_or_create_marital_status(validated_data.pop("marital_status"))
        validated_data.update({'base_clinic': facility, 'marital_status': marital_status})
        return super().update(instance, validated_data)

    def get_or_create_facility(self, facility_dict):
        facility = None
        try:
            facility = HealthFacility.objects.get(identification_code=facility_dict["identification_code"])
            # TODO update facility
        except HealthFacility.DoesNotExist:
            facility_type = self.get_or_create_facility_type(facility_dict["type"])
            facility = HealthFacility.objects.create(
                identification_code=facility_dict["identification_code"],
                name=facility_dict["name"],
                type=facility_type,
                longitude=facility_dict["longitude"],
                latitude=facility_dict["latitude"],
                address=facility_dict["address"]
            )
        return facility

    def get_or_create_facility_type(self, facility_type_dict):
        facility_type = None
        try:
            facility_type = FacilityType.objects.get(remote_id=facility_type_dict["id"])
            # TODO update facility type
        except FacilityType.DoesNotExist:
            facility_type = FacilityType.objects.create(
                remote_id=facility_type_dict["id"],
                level=facility_type_dict["level"],
                name=facility_type_dict["name"],
                description=facility_type_dict["description"]
            )
        return facility_type

    def get_or_create_marital_status(self, marital_status_dict):
        marital_status = None
        try:
            marital_status = MaritalStatus.objects.get(remote_id=marital_status_dict["id"])
            # TODO update marital status type
        except FacilityType.DoesNotExist:
            marital_status = MaritalStatus.objects.create(
                remote_id=marital_status_dict["id"],
                status=marital_status_dict["status"],
                description=marital_status_dict["description"],
                is_active=marital_status_dict["is_active"]
            )
        return marital_status
