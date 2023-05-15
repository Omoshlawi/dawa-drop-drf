from django.urls import path
from . import views
from rest_framework import routers

from .views import HealthFacilityViewSet, DeliveryModeViewSet, TransferRequestViewSet, \
    HealthFacilityTypeViewSet, MaritalStatusViewSet, AppointMentTypeViewSet, DeliveryTimeSlotViewSet

router = routers.DefaultRouter()
router.register(viewset=HealthFacilityViewSet, prefix='facilities', basename='facility')
router.register(viewset=MaritalStatusViewSet, prefix='marital-status', basename='marital-status')
router.register(viewset=DeliveryTimeSlotViewSet, prefix='delivery-time-slots', basename='time-slot')
router.register(viewset=AppointMentTypeViewSet, prefix='appointment-types', basename='appointment-types')
router.register(viewset=HealthFacilityTypeViewSet, prefix='facility-types', basename='facility-type')
router.register(viewset=TransferRequestViewSet, prefix='transfer-requests', basename='transfer-request')
router.register(viewset=DeliveryModeViewSet, prefix='deliver-mode', basename='mode')

app_name = 'core'
urlpatterns = [
    path('', views.ApiRootView.as_view(), name='root'),
]
urlpatterns.extend(router.urls)
