from django.urls import path, include
from rest_framework_nested import routers as nested_routers

from patients.views import PatientViewSet, PatientNextOfKeenViewSet, TriadViewSet

router = nested_routers.DefaultRouter()
router.register(prefix=r'', viewset=PatientViewSet, basename='patient')

next_of_keen = nested_routers.NestedDefaultRouter(router, r'', lookup='patient')
next_of_keen.register(prefix=r'next-of-keen', viewset=PatientNextOfKeenViewSet, basename='next-of-keen')

triad = nested_routers.NestedDefaultRouter(router, r'', lookup='patient')
triad.register(prefix='triads', viewset=TriadViewSet, basename='triad')
app_name = 'patients'

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(next_of_keen.urls)),
    path(r'', include(triad.urls))
]