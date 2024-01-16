from rest_framework import routers

from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from api.views import TitleViewSet

router = routers.DefaultRouter()
router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path(
        'redoc/',
        TemplateView.as_view(template_name='redoc.html'),
        name='redoc'
    ),
    path('api/', include(router.urls)),
]
