import requests
from django.conf import settings

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
