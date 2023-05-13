from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_nested import serializers as nested_serializer
from awards.serializers import PatientProgramEnrollmentSerializer, RedemptionSerializer
from core.models import HealthFacility, FacilityType, MaritalStatus, AppointMentType
from core.serializers import HealthFacilitySerializer, MaritalStatusSerializer
from doctors.models import Doctor
from medication.models import AppointMent, PatientHivMedication, ARTRegimen
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
    triads = serializers.JSONField()
    prescriptions = serializers.JSONField()
    appointments = serializers.JSONField()

    class Meta:
        model = Patient
        fields = (
            'patient_number', 'date_of_birth', 'county_of_residence', 'occupation',
            'national_id', 'marital_status', 'base_clinic', 'triads', 'next_of_keen',
            'prescriptions', 'appointments'
        )

    def update(self, instance, validated_data):
        facility = self.get_or_create_facility(validated_data.pop("base_clinic"))
        marital_status = self.get_or_create_marital_status(validated_data.pop("marital_status"))
        triads = validated_data.pop("triads")
        next_of_keen = validated_data.pop("next_of_keen")
        prescriptions = validated_data.pop('prescriptions')
        appointments = validated_data.pop('appointments')

        validated_data.update({'base_clinic': facility, 'marital_status': marital_status})
        updated_instance = super().update(instance, validated_data)
        self.update_or_create_triads(triads, updated_instance)
        self.update_or_create_nok(next_of_keen, updated_instance)
        self.update_or_create_appointments(appointments, updated_instance)
        self.update_or_create_prescriptions(prescriptions)
        return updated_instance

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
        except MaritalStatus.DoesNotExist:
            marital_status = MaritalStatus.objects.create(
                remote_id=marital_status_dict["id"],
                status=marital_status_dict["status"],
                description=marital_status_dict["description"],
                is_active=marital_status_dict["is_active"]
            )
        return marital_status

    def get_or_create_appointment_type(self, appointment_type_dict):
        try:
            appointment_typ = AppointMentType.objects.get(remote_id=appointment_type_dict["id"])
        except AppointMentType.DoesNotExist:
            appointment_typ = AppointMentType.objects.create(
                remote_id=appointment_type_dict["id"],
                type=appointment_type_dict["type"],
                description=appointment_type_dict["description"],
            )
        return appointment_typ

    def get_or_create_doctor(self, doctor_dict):
        """
        Checks of doctor exist else it creates a user and associates it with doctor
        """
        try:
            doctor = Doctor.obejcts.get(doctor_number=doctor_dict["doctor_number"])
        except Doctor.DoesNotExist:
            import secrets
            user = User.objects.create_user(
                username=doctor_dict["email"],
                email=doctor_dict["email"],
                password=secrets.token_hex(6),
                first_name=doctor_dict["first_name"],
                last_name=doctor_dict["last_name"]
            )
            profile = user.profile
            profile.user_type = 'doctor'
            doctor = Doctor.objects.create(
                user=user,
                doctor_number=doctor_dict["doctor_number"]
            )
        return doctor

    def get_or_create_regimen(self, regiment_dict):
        try:
            regimen = ARTRegimen.objects.get(remote_id=regiment_dict["id"])
        except ARTRegimen.DoesNotExist:
            regimen = ARTRegimen.objects.create(
                remote_id=regiment_dict["id"],
                regimen_line=regiment_dict["regimen_line"],
                regimen=regiment_dict["regimen"],
            )
        return regimen

    def update_or_create_triads(self, triads_dict, patient_instance):
        if triads_dict["count"] == 0:
            return
        for triad in triads_dict["list"]:
            try:
                Triad.objects.get(remote_id=triad["id"])
                # TODO perform update
            except Triad.DoesNotExist:
                # create
                Triad.objects.create(
                    remote_id=triad["id"],
                    patient=patient_instance,
                    weight=triad["weight"],
                    height=triad["height"],
                    temperature=triad["temperature"],
                    heart_rate=triad["heart_rate"],
                    blood_pressure=triad["blood_pressure"]
                )

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

    def update_or_create_appointments(self, appointments_dict, patient_instance):
        if appointments_dict["count"] == 0:
            return
        for appointment in appointments_dict["list"]:
            try:
                AppointMent.objects.get(remote_id=appointment["id"])
                # TODO perform update
            except AppointMent.DoesNotExist:
                AppointMent.objects.create(
                    remote_id=appointment["id"],
                    patient=patient_instance,
                    type=self.get_or_create_appointment_type(appointment["type"]),
                    doctor=self.get_or_create_doctor(appointment["doctor"]),
                    next_appointment_date=appointment["next_appointment_date"]
                )

    def update_or_create_prescriptions(self, prescriptions_dict, patient_instance):
        if prescriptions_dict["count"] == 0:
            return
        for prescription in prescriptions_dict["list"]:
            try:
                PatientHivMedication.objects.get(remote_id=prescription["id"])
                # TODO perform update
            except PatientHivMedication.DoesNotExist:
                PatientHivMedication.objects.create(
                    remote_id=prescription["id"],
                    patient=patient_instance,
                    regimen=self.get_or_create_regimen(prescription["regimen"]),
                    is_current=prescription["is_current"],
                    doctor=self.get_or_create_doctor(prescription["doctor"])
                )
