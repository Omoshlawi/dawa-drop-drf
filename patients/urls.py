from django.urls import path, include
from rest_framework_nested import routers as nested_routers

from patients.views import PatientViewSet, PatientNextOfKeenViewSet, AppointMentViewSet, MedicationViewSet, \
    PatientTriadViewSet, PatientTestViewSet, PatientSummaryViewSet

router = nested_routers.DefaultRouter()
router.register(prefix=r'prescriptions', viewset=MedicationViewSet, basename='prescription')
router.register(prefix=r'triads', viewset=PatientTriadViewSet, basename='triad')
router.register(prefix=r'test-results', viewset=PatientTestViewSet, basename='test-result')
router.register(prefix=r'summary', viewset=PatientSummaryViewSet, basename='summary')
router.register(prefix=r'appointments', viewset=AppointMentViewSet, basename='appointment')
router.register(prefix=r'', viewset=PatientViewSet, basename='patient')

next_of_keen = nested_routers.NestedDefaultRouter(router, r'', lookup='patient')
next_of_keen.register(prefix=r'next-of-keen', viewset=PatientNextOfKeenViewSet, basename='next-of-keen')

app_name = 'patients'

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(next_of_keen.urls)),
]
