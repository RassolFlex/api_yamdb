from rest_framework import routers
from django.urls import include, path

from .views import (GetTokenViewSet,
                    TitleViewSet,
                    GenreViewSet,
                    CategoryViewSet,
                    CustomUserViewSet,
                    SignupViewSet,
                    MeViewSet,
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
router_v1.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('v1/users/me/', MeViewSet.as_view({
        'get': 'retrieve',
        'patch': 'partial_update'
    }), name='me'),
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/',
         SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('v1/auth/token/', GetTokenViewSet.as_view({'post': 'create'}),
         name='get_token'),
]
