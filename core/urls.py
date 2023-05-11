from django.urls import path
from . import views
from rest_framework import routers

from .views import HealthFacilitySerializer, DeliveryModeViewSet, TransferRequestViewSet, \
    HealthFacilityTypeViewSet

router = routers.DefaultRouter()
router.register(viewset=HealthFacilitySerializer, prefix='facilities', basename='facility')
router.register(viewset=HealthFacilityTypeViewSet, prefix='facility-types', basename='facility-type')
router.register(viewset=TransferRequestViewSet, prefix='transfer-requests', basename='transfer-request')
router.register(viewset=DeliveryModeViewSet, prefix='deliver-mode', basename='mode')

app_name = 'core'
urlpatterns = [
    path('', views.ApiRootView.as_view(), name='root'),
]
urlpatterns.extend(router.urls)
