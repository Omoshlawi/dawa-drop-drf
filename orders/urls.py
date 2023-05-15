from rest_framework import routers
from django.urls import path

from .views import OrderViewSet, DeliveryFeedBackViewSet, DeliveryRequestViewSet

app_name = 'orders'
router = routers.DefaultRouter()
router.register(r'delivery-requests', DeliveryRequestViewSet, basename='delivery-request')
router.register(r'feedback', DeliveryFeedBackViewSet, basename='feedback')
router.register(r'', OrderViewSet, basename='order')

urlpatterns = router.urls
