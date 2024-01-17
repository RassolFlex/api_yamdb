from rest_framework import routers
from django.urls import include, path

from reviews.views import CommentViewSet, ReviewViewSet
from .views import TitleViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(
    '^titles/(?P<title_id>.+)/reviews', ReviewViewSet, basename='review'
)
router.register(
    '^titles/(?P<title_id>.+)/reviews/(?P<review_id>.+)/comments',
    CommentViewSet,
    basename='comment'
)

urlpatterns = [
    path('v1/', include(router.urls)),
]
