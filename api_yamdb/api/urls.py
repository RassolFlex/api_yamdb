from rest_framework import routers
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import TitleViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
    path('v1/auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
]
