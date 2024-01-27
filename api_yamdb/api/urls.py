from rest_framework import routers
from django.urls import include, path

from .views import (GetTokenViewSet,
                    TitleViewSet,
                    GenreViewSet,
                    CategoryViewSet,
                    ApiUserViewSet,
                    SignupAPIView,
                    # SignupViewSet,
                    # MeViewSet,
                    CommentViewSet,
                    ReviewViewSet)


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
router_v1.register(r'users', ApiUserViewSet, basename='users')

auth_patterns = [
    # path('signup/', SignupViewSet.as_view({'post': 'create'}), name='signup'),
    path('signup/', SignupAPIView.as_view(), name='signup'),
    path('token/', GetTokenViewSet.as_view({'post': 'create'}),
         name='get_token'),
]

urlpatterns = [
    path('v1/auth/', include(auth_patterns)),
    path('v1/', include(router_v1.urls)),
]
