from statistics import mean

from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework_simplejwt.tokens import AccessToken

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
        if ApiUser.objects.filter(
                email=data['email']).exists():
            user = ApiUser.objects.filter(
                email=data['email']).first()
            if data['username'] != user.username:
                raise serializers.ValidationError('Username already taken.')
        if ApiUser.objects.filter(
                username=data['username']).exists():
            user = ApiUser.objects.filter(
                username=data['username']).first()
            if data['email'] != user.email:
                raise serializers.ValidationError('Email already exists.')
        return data

    def create(self, validated_data):
        email = validated_data['email']
        if ApiUser.objects.filter(**validated_data).exists():
            user = ApiUser.objects.get(**validated_data)
            token = default_token_generator.make_token(user)
            send_mail(
                subject='confirmation_code',
                message=f'Your confirm code: "{token}"',
                from_email=None,
                recipient_list=[email],
                fail_silently=True,
            )
            return user
        user = ApiUser.objects.create(**validated_data)
        token = default_token_generator.make_token(user)
        send_mail(
            subject='confirmation_code',
            message=f'Your confirm code: "{token}"',
            from_email=None,
            recipient_list=[email],
            fail_silently=True,
        )
        return user


class ApiUserTokenSerializer(serializers.Serializer, ValidateUsernameMixin):

    username = serializers.CharField(
        max_length=LENGTH_FOR_FIELD, required=True
    )

    class Meta:
        model = ApiUser
        fields = (
            'username',
        )

    def create(self, validated_data):
        user = get_object_or_404(
            ApiUser, username=validated_data['username'])
        confirmation_code = validated_data.get('confirmation_code', False)
        if not confirmation_code:
            raise serializers.ValidationError('confirmation_code is empty')
        if not default_token_generator.check_token(user, confirmation_code):
            return serializers.ValidationError('invalid confirmation code')
        token = {'token': str(AccessToken.for_user(user))}
        return token


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
