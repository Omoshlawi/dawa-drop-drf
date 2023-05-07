from django.urls import path, include
from rest_framework import routers

from agents.views import DeliverAgentViewSet

app_name = "agents"
router = routers.DefaultRouter()
router.register(prefix=r'agents', viewset=DeliverAgentViewSet, basename='agent')


urlpatterns = [
    path(r'', include(router.urls)),
]