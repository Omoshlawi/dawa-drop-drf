from django.urls import path, include
from rest_framework import routers

from users.views import (
    UserViewSet,
)
from rest_framework_nested import routers as nested_routers

router = routers.DefaultRouter()

router.register(prefix=r'', viewset=UserViewSet, basename='user')

app_name = 'users'
urlpatterns = [
    path(r'', include(router.urls)),
]
