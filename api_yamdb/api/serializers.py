from statistics import mean
import re

from rest_framework import serializers

from reviews.models import (Category,
                            CustomUser,
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


class CustomUserSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def create(self, validated_data):
        return CustomUser.objects.create()

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Username should not be equal "me".')
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, username):
            raise serializers.ValidationError('Invalid username.')
        return username


class SignupSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email'
        )

        # validators = [
        #     UniqueTogetherValidator(
        #         queryset=CustomUser.objects.all(),
        #         fields=('username', 'email'),
        #         message='Email is invalid.'
        #     )
        # ]

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError(
                'Username should not be equal "me".')
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, username):
            raise serializers.ValidationError('Invalid username.')
        return username


class CustomUserTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        fields = (
            'username',
        )


class UserMeSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomUser
        read_only_fields = ('role',)
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )

    def validate_username(self, username):
        if not username:
            raise serializers.ValidationError('Username must be not empty.')
        if len(username) > 150:
            raise serializers.ValidationError('Username over 150 length.')
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, username):
            raise serializers.ValidationError('Invalid username.')
        return username


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
