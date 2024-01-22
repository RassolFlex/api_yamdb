from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, mixins, status, viewsets, permissions
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied, MethodNotAllowed
from rest_framework.decorators import action
from rest_framework_simplejwt.tokens import AccessToken
from django_filters.rest_framework import DjangoFilterBackend

from reviews.models import Category, CustomUser, Genre, Title
from .permissions import IsAdminOrReadOnly, AdminOnly
from .serializers import (TitleSerializer,
                          GenreSerializer,
                          CategorySerializer,
                          CustomUserSerializer,
                          CreateCustomUserSerializer,
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
    serializer_class = TitleSerializer
    permission_classes = [IsAdminOrReadOnly]
    pagination_class = PageNumberPagination

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
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = '__all__'
    pagination_class = LimitOffsetPagination
    permission_classes = [AdminOnly]

    def list(self, request):
        if request.data.get('role') == 'admin':
            return super().list(self)

    def create(self, request, *args, **kwargs):
        serializer = CustomUserSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_201_CREATED)

    # def update(self, request, username, pk=None):
    #     return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # def get_permissions(self):
    #     """
    #     Instantiates and returns the list of permissions that this view requires.
    #     """
    #     if self.action == 'list':
    #         permission_classes = [permissions.IsAdminUser]
    #     elif self.action == 'retrieve':
    #         permission_classes = [permissions.IsAdminUser]
    #     elif self.action == 'detail':
    #         permission_classes = [permissions.IsAdminUser]
    #     else:
    #         permission_classes = [permissions.IsAuthenticated]
    #     return [permission() for permission in permission_classes]


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
    serializer_class = CreateCustomUserSerializer

    def create(self, request):
        serializer = CreateCustomUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = request.data['email']
        username = request.data['username']
        if CustomUser.objects.filter(email=email).first() is not None:
            if CustomUser.objects.filter(username=username).first() is None:
                return Response(
                    {'email': 'user with this email already exist'},
                    status=status.HTTP_400_BAD_REQUEST)
        if CustomUser.objects.filter(username=username).first() is not None:
            if CustomUser.objects.filter(
                    username=username).first().email != email:
                return Response({'email': 'invalid email'},
                                status=status.HTTP_400_BAD_REQUEST)
        if username == 'me':
            return Response({'username': 'username "me" not allowed'},
                            status=status.HTTP_400_BAD_REQUEST)
        CustomUser.objects.get_or_create(username=username, email=email)
        send_mail(
            subject='confirmation_code',
            message=f'Your confirm code: "{username}confirmcode"',
            from_email='yamdb@yamdb.api',
            recipient_list=[email],
            fail_silently=True,
        )
        return Response(request.data, status=status.HTTP_200_OK)


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
