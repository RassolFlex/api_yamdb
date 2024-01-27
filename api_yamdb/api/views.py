from django.core.exceptions import BadRequest
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters,
                            mixins,
                            status,
                            viewsets,
                            permissions)
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.generics import CreateAPIView

from reviews.models import (Category,
                            Comment,
                            ApiUser,
                            Genre,
                            Review,
                            Title)
from .permissions import (AdminOnly,
                          IsAdminOrReadOnly,
                          PermissionForReviewsAndComments)
from .serializers import (CommentSerializer,
                          ReviewSerializer,
                          TitleSerializerForRead,
                          TitleSerializerForWrite,
                          GenreSerializer,
                          CategorySerializer,
                          ApiUserSerializer,
                          SignupSerializer,
                          ApiUserTokenSerializer,
                          UserDetailSerializer)


class DestroyCreateListViewSet(mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
                               mixins.UpdateModelMixin,
                               viewsets.GenericViewSet):
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    permission_classes = [IsAdminOrReadOnly]

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionDenied('')
        serializer.save()

    def perform_update(self, serializer):
        raise MethodNotAllowed(method='patch')


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializerForWrite
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'id'
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('genre', 'category', 'year',)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return TitleSerializerForWrite
        return TitleSerializerForRead

    def filter_queryset(self, queryset):
        if self.request.query_params:
            filters = {}
            for key, value in self.request.query_params.items():
                if key == 'category' or key == 'genre':
                    filters[f'{key}__slug'] = value
                    continue
                filters[key] = value
            try:
                return queryset.filter(**filters)
            except ValueError:
                return super().filter_queryset(queryset)
        return super().filter_queryset(queryset)

    def perform_create(self, serializer):
        if self.request.user.role != 'admin':
            raise PermissionDenied('')
        serializer.save()

    def perform_update(self, serializer):
        if self.request.method == 'PUT':
            raise MethodNotAllowed(method='put')
        if self.request.user.role != 'admin':
            raise MethodNotAllowed(method='patch')
        serializer.save()


class GenreViewSet(DestroyCreateListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    http_method_names = ['get', 'post', 'delete']

    def get_permissions(self):
        if self.request.method == 'GET':
            self.permission_classes = [permissions.IsAuthenticatedOrReadOnly]
        else:
            self.permission_classes = [AdminOnly]
        return super(GenreViewSet, self).get_permissions()


class CategoryViewSet(DestroyCreateListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ApiUserViewSet(viewsets.ModelViewSet):
    queryset = ApiUser.objects.all()
    serializer_class = ApiUserSerializer
    lookup_field = 'username'
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('username',)
    ordering_fields = ('username',)
    pagination_class = LimitOffsetPagination
    permission_classes = [AdminOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(methods=['GET', 'PATCH'],
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            url_path='me')
    def get_detail_user(self, request):
        serializer = ApiUserSerializer(request.user)
        if request.method == 'PATCH':
            if request.user.role == 'user':
                serializer = UserDetailSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            else:
                serializer = ApiUserSerializer(
                    request.user,
                    data=request.data,
                    partial=True
                )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data=serializer.data)


class SignupAPIView(CreateAPIView):
    serializer_class = SignupSerializer

    def create(self, request, *args, **kwargs):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=request.data)


class GetTokenAPIView(CreateAPIView):
    serializer_class = ApiUserTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = ApiUserTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(data=request.data)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (PermissionForReviewsAndComments,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        if (
            self.get_queryset().filter(
                author=self.request.user
            ).first() is not None
        ):
            raise BadRequest('Review with this author to title already exist.')
        serializer.save(author=self.request.user, title=self.get_title())

    def perform_update(self, serializer):
        if (
            self.request.user.role != 'user'
            or Review.objects.get(pk=self.kwargs.get('pk')).author
            == self.request.user
        ):
            return super(ReviewViewSet, self).perform_update(serializer)
        raise PermissionDenied('Cannot change someone\'s review.')

    def perform_destroy(self, instance):
        if (
            self.request.user.role != 'user'
            or Review.objects.get(pk=self.kwargs.get('pk')).author
            == self.request.user
        ):
            return super().perform_destroy(instance)
        raise PermissionDenied('Cannot delete someone\'s review.')


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (PermissionForReviewsAndComments,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(Review, pk=self.kwargs.get('review_id'))

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())

    def perform_update(self, serializer):
        if (
            self.request.user.role != 'user'
            or Comment.objects.get(pk=self.kwargs.get('pk')).author
            == self.request.user
        ):
            return super(CommentViewSet, self).perform_update(serializer)
        raise PermissionDenied('Cannot change someone\'s review.')

    def perform_destroy(self, instance):
        if (
            self.request.user.role != 'user'
            or Comment.objects.get(pk=self.kwargs.get('pk')).author
            == self.request.user
        ):
            return super().perform_destroy(instance)
        raise PermissionDenied('Cannot delete someone\'s review.')
