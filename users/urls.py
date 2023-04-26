from django.urls import path, include
from rest_framework import routers

from users.views import UserViewSet

router = routers.DefaultRouter()
# base name `user` is used for hyperlink in serializers HyperlinkedIdentityField
# user view name `user`-detail
router.register(r'', UserViewSet, basename='user')
app_name = 'users'
urlpatterns = router.urls