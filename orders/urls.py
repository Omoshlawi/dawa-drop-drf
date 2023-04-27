from rest_framework import routers
from django.urls import path

from .views import OrderViewSet, DeliveryFeedBackViewSet, DeliveryViewSet

app_name = 'orders'
router = routers.DefaultRouter()
router.register(r'delivery', DeliveryViewSet, basename='delivery')
router.register(r'feedback', DeliveryFeedBackViewSet, basename='feedback')
router.register(r'', OrderViewSet, basename='order')

urlpatterns = router.urls
