from django.db.models import Avg
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import (filters,
                            mixins,
                            status,
                            viewsets,
                            permissions)
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken

from reviews.models import (Category,
                            CustomUser,
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
                          CustomUserSerializer,
                          SignupSerializer,
                          CustomUserTokenSerializer,
                          UserMeSerializer)
from .filters import TitleSearchFilter


class DestroyCreateListViewSet(mixins.ListModelMixin,
                               mixins.DestroyModelMixin,
                               mixins.CreateModelMixin,
                               viewsets.GenericViewSet):
    lookup_field = 'slug'
    pagination_class = PageNumberPagination
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('name',)
    search_fields = ('name',)
    permission_classes = (IsAdminOrReadOnly,)


class CustomCreateViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all().annotate(rating=Avg('reviews__score'))
    serializer_class = TitleSerializerForWrite
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend, filters.OrderingFilter)
    filterset_class = TitleSearchFilter
    ordering_fields = ('genre', 'category', 'year',)
    filterset_fields = ('genre', 'category', 'year',)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method not in permissions.SAFE_METHODS:
            return TitleSerializerForWrite
        return TitleSerializerForRead


class GenreViewSet(DestroyCreateListViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(DestroyCreateListViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class CustomUserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    lookup_field = 'username'
    filter_backends = (filters.OrderingFilter, filters.SearchFilter)
    search_fields = ('username',)
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    permission_classes = [AdminOnly]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def create(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        CustomUser.objects.get_or_create(
            username=request.data['username'], email=request.data['email']
        )
        return Response(data=request.data, status=status.HTTP_201_CREATED)


class MeViewSet(mixins.RetrieveModelMixin,
                mixins.UpdateModelMixin,
                viewsets.GenericViewSet):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return get_object_or_404(CustomUser,
                                 username=self.request.user.username)


class SignupViewSet(CustomCreateViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = SignupSerializer

    def create(self, request):
        if CustomUser.objects.filter(
                username=request.data.get('username')).first() is not None:
            user = CustomUser.objects.filter(
                username=request.data.get('username')).first()
            email = request.data['email']
            if user.email != email:
                return Response({'email': 'invalid email'},
                                status=status.HTTP_400_BAD_REQUEST)
            username = request.data['username']
            send_mail(
                subject='confirmation_code',
                message=f'Your confirm code: "{username}confirmcode"',
                from_email='yamdb@yamdb.api',
                recipient_list=[email],
                fail_silently=True,
            )
            return Response(data=request.data, status=status.HTTP_200_OK)
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data['email']
        username = request.data['username']
        user = CustomUser.objects.get_or_create(username=username, email=email)
        send_mail(
            subject='confirmation_code',
            message=f'Your confirm code: "{username}confirmcode"',
            from_email='yamdb@yamdb.api',
            recipient_list=[email],
            fail_silently=True,
        )
        return Response(data=request.data, status=status.HTTP_200_OK)


class GetTokenViewSet(CustomCreateViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserTokenSerializer

    def create(self, request, *args, **kwargs):
        serializer = CustomUserTokenSerializer(data=request.data)
        serializer.is_valid()
        username = request.data.get('username', False)
        if not username:
            return Response({'username': 'username is empty'},
                            status=status.HTTP_400_BAD_REQUEST)
        user = get_object_or_404(
            CustomUser, username=username)
        expected_conf_code = f'{username}confirmcode'
        confirmation_code = request.data.get('confirmation_code', False)
        if not confirmation_code:
            return Response({
                'confirmation_code': 'confirmation_code is empty'},
                status=status.HTTP_400_BAD_REQUEST)
        if confirmation_code != expected_conf_code:
            return Response({'confirmation_code': 'invalid confirmation code'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = {'token': str(AccessToken.for_user(user))}
        return Response(token, status=status.HTTP_200_OK)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (PermissionForReviewsAndComments,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_title(self):
        return get_object_or_404(Title, pk=self.kwargs.get('title_id'))

    def get_queryset(self):
        return self.get_title().reviews.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (PermissionForReviewsAndComments,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_review(self):
        return get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id'),
            title=self.kwargs.get('title_id')
        )

    def get_queryset(self):
        return self.get_review().comments.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())
