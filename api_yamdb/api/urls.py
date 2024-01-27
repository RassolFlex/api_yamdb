from rest_framework import routers
from django.urls import include, path

from .views import (TitleViewSet,
                    GenreViewSet,
                    CategoryViewSet,
                    ApiUserViewSet,
                    SignupAPIView,
                    GetTokenAPIView,
                    CommentViewSet,
                    ReviewViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet, basename='title')
router_v1.register(r'genres', GenreViewSet, basename='genre')
router_v1.register(r'categories', CategoryViewSet, basename='category')
router_v1.register(
    '^titles/(?P<title_id>.+)/reviews', ReviewViewSet, basename='review'
)
router_v1.register(
    '^titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    CommentViewSet,
    basename='comment'
)
router_v1.register(r'users', ApiUserViewSet, basename='users')

auth_patterns = [
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('token/', GetTokenAPIView.as_view(), name='get_token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include(router_v1.urls)),
]
