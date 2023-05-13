from rest_framework import routers
from django.urls import path

app_name = 'medication'

from .views import (
    AppointMentViewSet,
    HIVLabTestViewSet, ARTRegimenViewSet, PatientHivMedicationViewSet, PatientHIVLabTestViewSet
)

router = routers.DefaultRouter()
router.register(prefix=r'appointments', viewset=AppointMentViewSet, basename='appointment')
router.register(prefix=r'regimens', viewset=ARTRegimenViewSet, basename='regimen')
router.register(prefix=r'patient-tests', viewset=PatientHIVLabTestViewSet, basename='test')
router.register(prefix=r'', viewset=PatientHivMedicationViewSet, basename='patient-hiv-prescription')

urlpatterns = router.urls
