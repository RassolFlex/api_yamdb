from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAdminUser

from reviews.models import Title, Genre, Category, CustomUser
from .serializers import TitleSerializer, GenreSerializer, CategorySerializer, CustomUserSerializer
from .permissions import IsAuthorOrReadOnly


class DestroyCreateListViewSet(mixins.ListModelMixin,
                              mixins.DestroyModelMixin,
                              mixins.CreateModelMixin,
                              viewsets.GenericViewSet):
    def get_permissions(self):
        if self.action == 'create':
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [IsAuthorOrReadOnly]
        return [permission() for permission in permission_classes]



class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = [IsAuthorOrReadOnly]


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination


class GenreViewSet(DestroyCreateListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = [IsAuthorOrReadOnly]


class CategoryViewSet(DestroyCreateListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthorOrReadOnly]
