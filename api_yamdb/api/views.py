from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination

from reviews.models import Title, Genre, Category, CustomUser
from .serializers import TitleSerializer, GenreSerializer, CategorySerializer, CustomUserSerializer


class DestroyPatchListViewSet(mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.UpdateModelMixin,
                              viewsets.GenericViewSet):
    pass


class TitleViewSet(DestroyPatchListViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination

class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
