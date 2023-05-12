from patients.models import Patient
from patients.serializers import PatientAddUpdateSerializer
from users.serializers import UserSerializer, ProfileSerializer


def obscure_email(email):
    username, domain = email.split("@")
    obscured_email = '{}{}@{}'.format(username[:2], '*' * len(username[2:]), domain)
    return obscured_email


def obscure_number(phone_number):
    obscured_number = '{}*******{}'.format(phone_number[:4], phone_number[-2:])
    return obscured_number


def update_patient(patient, request):
    # update user
    user = request.user
    user_serializer = UserSerializer(instance=user, data=patient)
    user_serializer.is_valid(raise_exception=True)
    user = user_serializer.save()
    # update profile
    profile_serializer = ProfileSerializer(instance=user.profile, data=patient)
    profile_serializer.is_valid(raise_exception=True)
    profile = profile_serializer.save()
    # update patient
    p = Patient.objects.get_or_create(
        user=user
    )[0]
    patient_serializer = PatientAddUpdateSerializer(instance=p, data=patient)
    patient_serializer.is_valid(raise_exception=True)
    patient = patient_serializer.save()


