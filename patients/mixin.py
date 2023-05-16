from django.contrib.auth.models import User
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.response import Response

from awards.serializers import PatientProgramEnrollmentSerializer, RedemptionSerializer
from core import permisions as custom_permissions
from core.models import AppointMentType, HealthFacility, FacilityType
from doctors.models import Doctor
from patients.models import Patient, AppointMent


class LoyaltyPointsMixin:
    @action(
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permissions.IsPatient,
            custom_permissions.HasRelatedUserType
        ],
        methods=['get'],
        url_path='points',
        url_name='points',
        detail=True
    )
    def points(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'])
        data = {
            'total': patient.total_points,
            'total_redeemed_points': patient.total_redemption_points,
            'redeem_count': patient.redemptions.all().count(),
            'redeemable_points': patient.points_balance,
            'current_program_enrolment': PatientProgramEnrollmentSerializer(
                instance=patient.current_program_enrollment,
                context={'request': request}
            ).data if patient.current_program_enrollment is not None else None,
            'redeem_list': RedemptionSerializer(
                instance=patient.redemptions.all(),
                many=True,
                context={'request': request}
            ).data
        }
        return Response(data)

    @action(
        permission_classes=[
            permissions.IsAuthenticated,
            custom_permissions.IsPatient,
            custom_permissions.HasRelatedUserType
        ],
        methods=['post'],
        url_path='redeem-points',
        url_name='redeem-points',
        detail=True,
        serializer_class=RedemptionSerializer
    )
    def redeem(self, request, *args, **kwargs):
        patient = get_object_or_404(Patient, id=kwargs['pk'], user=request.user)
        serializer = RedemptionSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        # TODO CHECK IF MAX REDEMPTION REACHED IN EITHER SERIALIZER validator or here
        points_redeemed = serializer.validated_data.get("reward").point_value
        instance = serializer.save(patient=patient, points_redeemed=points_redeemed)
        data = {
            'total': patient.total_points,
            'total_redeemed_points': patient.total_redemption_points,
            'redeem_count': patient.redemptions.all().count(),
            'redeemable_points': patient.points_balance,
            'program_enrolments': PatientProgramEnrollmentSerializer(
                instance=patient.enrollments,
                many=True,
                context={'request': request}
            ).data,
            'current_program_enrolment': PatientProgramEnrollmentSerializer(
                instance=patient.current_program_enrollment,
                context={'request': request}
            ).data if patient.current_program_enrollment is not None else None,
            'redemption': RedemptionSerializer(instance=instance, context={'request': request}).data
        }
        return Response(data)


class PatientAppointmentSyncMixin:
    def update_or_create_appointments(self, appointments_dict, patient_instance):
        if appointments_dict["count"] == 0:
            return
        for appointment in appointments_dict["list"]:
            try:
                appointment_instance = AppointMent.objects.get(remote_id=appointment["id"])
                # TODO perform update
            except AppointMent.DoesNotExist:
                appointment_instance = AppointMent.objects.create(
                    remote_id=appointment["id"],
                    patient=patient_instance,
                    type=self.get_or_create_appointment_type(appointment["type"]),
                    doctor=self.get_or_create_doctor(appointment["doctor"]),
                    next_appointment_date=appointment["next_appointment_date"]
                )

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
            doctor = Doctor.objects.get(doctor_number=doctor_dict["doctor_number"])
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


class FacilitySyncMixin:
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
