from django.urls import path, include
from rest_framework import routers
from users.views import UserViewSet

router = routers.DefaultRouter()
# router.register(prefix=r'patients', viewset=UserViewSet, basename='patient')
# router.register(prefix=r'doctors', viewset=UserViewSet, basename='doctor')
# router.register(prefix=r'agents', viewset=UserViewSet, basename='agent')
router.register(prefix=r'', viewset=UserViewSet, basename='user')

app_name = 'users'
urlpatterns = [
    path(r'', include(router.urls)),
]
