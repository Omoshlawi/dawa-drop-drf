from django.urls import path, include
from rest_framework import routers
from users.views import (
    UserViewSet, DeliverAgentViewSet,
    DoctorsViewSet, PatientViewSet,
    PatientNextOfKeenViewSet
)
from rest_framework_nested import routers as nested_routers

router = nested_routers.DefaultRouter()
router.register(prefix=r'patients', viewset=PatientViewSet, basename='patient')
router.register(prefix=r'doctors', viewset=DoctorsViewSet, basename='doctor')
router.register(prefix=r'agents', viewset=DeliverAgentViewSet, basename='agent')
router.register(prefix=r'', viewset=UserViewSet, basename='user')

next_of_keen = nested_routers.NestedDefaultRouter(router, r'patients', lookup='patient')
next_of_keen.register(prefix=r'next-of-keen', viewset=PatientNextOfKeenViewSet, basename='next-of-keen')

app_name = 'users'
urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(next_of_keen.urls))
]
