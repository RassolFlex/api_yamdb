from rest_framework import status, viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404

from reviews.models import Title, Genre, Category, CustomUser
from .serializers import (TitleSerializer,
                          GenreSerializer,
                          CategorySerializer,
                          CustomUserSerializer,
                          CreateCustomUserSerializer,
                          CustomUserTokenSerializer)


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


class CustomCreateViewSet(mixins.CreateModelMixin,
                          viewsets.GenericViewSet):
    pass


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
        username = request.POST.get('username', False)
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


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
