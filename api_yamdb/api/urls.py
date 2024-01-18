from rest_framework import routers
from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from reviews.views import CommentViewSet, ReviewViewSet
from .views import (TitleViewSet,
                    GenreViewSet,
                    CategoryViewSet,
                    CustomUserViewSet,
                    SignupViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'genres', GenreViewSet)
router_v1.register(r'categories', CategoryViewSet)
router_v1.register(
    '^titles/(?P<title_id>.+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    '^titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register(r'users', CustomUserViewSet)
router_v1.register('auth/signup', SignupViewSet, basename='signup')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/token/', TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('v1/auth/token/refresh/', TokenRefreshView.as_view(),
         name='token_refresh'),
]
