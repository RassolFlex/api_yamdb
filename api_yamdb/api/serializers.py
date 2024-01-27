from statistics import mean

from django.core.exceptions import BadRequest
from rest_framework import serializers
from django.core.mail import send_mail
from rest_framework.response import Response
from rest_framework import status

from reviews.constants import (LENGTH_FOR_FIELD,
                               LENGTH_FOR_FIELD_EMAIL)
from reviews.models import (Category,
                            ApiUser,
                            Genre,
                            Title,
                            GenreTitle,
                            Comment,
                            Review)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializerForWrite(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def create(self, validated_data):
        genre_data = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for genre in genre_data:
            current_genre, status = Genre.objects.get_or_create(
                slug=genre
            )
            GenreTitle.objects.create(genre=current_genre, title=title)
        return title

    def get_rating(self, obj):
        reviews = Title.objects.get(id=obj.id).reviews
        scores = [score['score'] for score in reviews.values('score')]
        if len(scores) == 0:
            return None
        return int(mean(scores))


class TitleSerializerForRead(serializers.ModelSerializer):
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category',
        )

    def get_rating(self, obj):
        reviews = Title.objects.get(id=obj.id).reviews
        scores = [score['score'] for score in reviews.values('score')]
        if len(scores) == 0:
            return None
        return int(mean(scores))


class ValidateUsernameMixin:
    def validate_username(self, username):
        return ApiUser.check_username(username)


class ApiUserSerializer(serializers.ModelSerializer, ValidateUsernameMixin):

    class Meta:
        model = ApiUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class SignupSerializer(serializers.Serializer, ValidateUsernameMixin):

    username = serializers.CharField(
        max_length=LENGTH_FOR_FIELD, required=True
    )
    email = serializers.EmailField(
        max_length=LENGTH_FOR_FIELD_EMAIL, required=True
    )

    class Meta:
        model = ApiUser
        fields = (
            'username',
            'email'
        )

    def validate(self, data):
        username = data['username']
        if ApiUser.objects.filter(
                email=data.get('email')).first() is not None:
            user = ApiUser.objects.filter(
                email=data.get('email')).first()
            if username != user.username:
                print('калечный респондс')
                # raise BadRequest('калечный респондс.')
                return Response(
                    {'email': 'invalid email'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return data

    def create(self, validated_data):
        # if ApiUser.objects.filter(
        #         username=validated_data.get('username')).first() is not None:
        #     user = ApiUser.objects.filter(
        #         username=validated_data.get('username')).first()
        #     email = validated_data['email']
        #     if user.email != email:
        #         return Response({'email': 'invalid email'},
        #                         status=status.HTTP_400_BAD_REQUEST)
        #     username = validated_data['username']
        #     send_mail(
        #         subject='confirmation_code',
        #         message=f'Your confirm code: "{username}confirmcode"',
        #         from_email='yamdb@yamdb.api',
        #         recipient_list=[email],
        #         fail_silently=True,
        #     )
        #     return Response(data=validated_data, status=status.HTTP_200_OK)
        serializer = SignupSerializer(data=validated_data)
        serializer.is_valid(raise_exception=True)
        email = validated_data['email']
        username = validated_data['username']
        # if ApiUser.objects.filter(
        #         email=validated_data.get('email')).first() is not None:
        #     user = ApiUser.objects.filter(
        #         email=validated_data.get('email')).first()
        #     if username != user.username:
        #         print('калечный респондс')
        #         # raise BadRequest('калечный респондс.')
        #         return Response(
        #             {'email': 'invalid email'},
        #             status=status.HTTP_400_BAD_REQUEST
        #         )
        user = ApiUser.objects.get_or_create(**validated_data)
        send_mail(
            subject='confirmation_code',
            message=f'Your confirm code: "{username}confirmcode"',
            from_email='yamdb@yamdb.api',
            recipient_list=[email],
            fail_silently=True,
        )
        return Response(data=validated_data, status=status.HTTP_200_OK)


class ApiUserTokenSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=LENGTH_FOR_FIELD, required=True
    )

    class Meta:
        model = ApiUser
        fields = (
            'username',
        )


class UserDetailSerializer(ApiUserSerializer):

    class Meta(ApiUserSerializer.Meta):
        read_only_fields = ('role',)


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title',)
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(
        read_only=True, default=serializers.CurrentUserDefault()
    )

    class Meta:
        fields = '__all__'
        read_only_fields = ('title', 'review', 'pub_date')
        model = Comment
