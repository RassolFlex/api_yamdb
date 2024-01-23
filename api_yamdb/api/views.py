from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets, permissions
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, CustomUser, Genre, Title
from .permissions import IsAdminOrReadOnly, AdminOnly
from .serializers import (TitleSerializerForRead,
                          TitleSerializerForWrite,
                          GenreSerializer,
                          CategorySerializer,
                          CustomUserSerializer,
                          SignupSerializer,
                          CustomUserTokenSerializer,
                          UserMeSerializer)


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


class CustomCreateViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    pass


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializerForWrite
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action == 'create':
            return TitleSerializerForWrite
        return TitleSerializerForRead

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
    permission_classes = [permissions.IsAuthenticated,]

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
                return Response(status=status.HTTP_400_BAD_REQUEST)
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
        if user:
            return Response(data=request.data, status=status.HTTP_200_OK)
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
        if request.data['confirmation_code'] != expected_conf_code:
            return Response({'confirmation_code': 'invalid confirmation code'},
                            status=status.HTTP_400_BAD_REQUEST)
        token = {'token': str(AccessToken.for_user(user))}
        return Response(token, status=status.HTTP_200_OK)
