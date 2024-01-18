from rest_framework import viewsets, mixins, filters
from rest_framework.pagination import LimitOffsetPagination
from django.core.mail import send_mail
from django.http.response import JsonResponse

from reviews.models import Title, Genre, Category, CustomUser
from .serializers import (TitleSerializer,
                          GenreSerializer,
                          CategorySerializer,
                          CustomUserSerializer)


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
    serializer_class = CustomUserSerializer

    def create(self, request):
        email = self.request.data['email']
        username = self.request.data['username']
        send_mail(
            subject='confirmation_code',
            message=f'Your confirm code: "{username}confirmcode"',
            from_email='yamdb@yamdb.api',
            recipient_list=[email],
            fail_silently=True,
        )
        return JsonResponse(data=self.request.data)


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
