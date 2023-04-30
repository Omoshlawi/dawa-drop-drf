from rest_framework import routers

from awards.views import LoyaltyProgramViewSet, RewardViewSet

router = routers.DefaultRouter()
router.register(r'rewards', RewardViewSet, basename='reward')
router.register(r'', LoyaltyProgramViewSet, basename='program')

app_name = "awards"

urlpatterns = router.urls
