from django.urls import path
from . import views
from rest_framework import routers

from .views import HIVClinicViewSet, DeliveryModeViewSet, TransferRequestViewSet

router = routers.DefaultRouter()
router.register(viewset=HIVClinicViewSet, prefix='clinics', basename='clinic')
router.register(viewset=TransferRequestViewSet, prefix='transfer-requests', basename='transfer-request')
router.register(viewset=DeliveryModeViewSet, prefix='deliver-mode', basename='mode')

app_name = 'core'
urlpatterns = [
    path('', views.ApiRootView.as_view(), name='root'),
]
urlpatterns.extend(router.urls)
