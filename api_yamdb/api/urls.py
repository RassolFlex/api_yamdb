from rest_framework import routers
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import TitleViewSet, CustomUserViewSet

router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
]
