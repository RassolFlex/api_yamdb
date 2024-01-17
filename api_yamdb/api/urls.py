from rest_framework import routers
from django.urls import include, path

from .views import TitleViewSet, GenreViewSet, CategoryViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'categories', CategoryViewSet)

urlpatterns = [
    path('v1/', include(router.urls)),
]