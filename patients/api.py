import requests
from django.conf import settings
from django.utils import timezone
from patients.mixin import PatientAppointmentSyncMixin
from patients.models import AppointMent


def get_and_sync_appointments(patient):
    url = f"{settings.EMR_BASE_URL}medication/appointments/"
    response = requests.get(url=url, params={'patient__patient_number': patient.patient_number})
    data = response.json()
    if data['count'] == 0:
        return
    data["list"] = data.pop("results")
    mixin = PatientAppointmentSyncMixin()
    mixin.update_or_create_appointments(data, patient)


def get_prescriptions(patient):
    url = f"{settings.EMR_BASE_URL}medication/"
    response = requests.get(url, params={'patient__patient_number': patient.patient_number}).json()
    response['results'] = map(
        lambda prescription: {
            "id": prescription["id"],
            "regimen": {
                "id": prescription["regimen"]["id"],
                "regimen_line": prescription["regimen"]["regimen_line"],
                "regimen": prescription["regimen"]["regimen"],
            },
            "doctor": prescription["doctor"],
            "is_current": prescription["is_current"],
            "created_at": prescription["created_at"],
            "updated_at": prescription["updated_at"],

        },
        response['results']
    )
    return response


def get_remote_current_prescription(patient):
    current_prescriptions = sorted(
        filter(
            lambda prescription: prescription["is_current"] == True,
            get_prescriptions(patient)['results']
        ),
        key=lambda pres: timezone.datetime.fromisoformat(pres["created_at"]),
        reverse=True
    )
    if len(current_prescriptions):
        return current_prescriptions[0]
    return None


def get_triads(patient):
    url = f"{settings.EMR_BASE_URL}medication/patients-triads/"
    response = requests.get(url=url, params={'patient__patient_number': patient.patient_number}).json()
    response['results'] = map(
        lambda triad: {
            'id': triad["id"],
            'weight': triad["weight"],
            'height': triad["height"],
            'temperature': triad["temperature"],
            'heart_rate': triad["heart_rate"],
            'blood_pressure': triad["blood_pressure"],
            'created_at': triad["created_at"],
        },
        response['results']
    )
    return response


def get_tests(patient):
    url = f"{settings.EMR_BASE_URL}medication/test/"
    response = requests.get(url=url, params={'appointment__patient__patient_number': patient.patient_number}).json()
    response['results'] = map(
        lambda test: {
            'id': test["id"],
            'cd4_count': test["cd4_count"],
            'viral_load': test["viral_load"],
            'created_at': test["created_at"],
        },
        response['results']
    )
    return response


def get_patient_summary_statistics():
    url = f'{settings.EMR_BASE_URL}users/summary/'
    resp = requests.get(url)
    return resp.json()
