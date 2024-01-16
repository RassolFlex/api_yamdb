from rest_framework import routers
from django.urls import include, path

from .views import TitleViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('', include(router.urls)),
]