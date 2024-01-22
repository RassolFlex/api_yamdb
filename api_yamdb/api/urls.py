from rest_framework import routers
from django.urls import include, path

from reviews.views import CommentViewSet, ReviewViewSet
from .views import (GetTokenViewSet,
                    TitleViewSet,
                    GenreViewSet,
                    CategoryViewSet,
                    CustomUserViewSet,
                    SignupViewSet,
                    MeViewSet)


router_v1 = routers.DefaultRouter()
router_v1.register(r'titles', TitleViewSet)
router_v1.register(r'titles/(?P<title_id>\d+)', TitleViewSet)
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

urlpatterns = [
    path('v1/users/me/', MeViewSet.as_view({'get': 'list'}), name='me'),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/',
         SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('v1/auth/token/', GetTokenViewSet.as_view({'post': 'create'}),
         name='get_token'),
]
