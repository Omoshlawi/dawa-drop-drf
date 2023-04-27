from django.urls import path, include
from rest_framework import routers
from users.views import UserViewSet

router = routers.DefaultRouter()
router.register(prefix=r'', viewset=UserViewSet, basename='user')

app_name = 'users'
urlpatterns = [
    path(r'', include(router.urls)),
]
