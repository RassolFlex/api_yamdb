from statistics import mean
import re

from rest_framework import serializers

from reviews.models import Category, CustomUser, Genre, Title, GenreTitle


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
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

    def create(self, validated_data):
        category = self.initial_data['category']
        category = Category.objects.get(slug=category)
        category = Category.objects.get(pk=category.id)
        genre_data = self.initial_data['genre']
        validated_data['category'] = category
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

    # username = serializers.RegexField(
    #     regex=r'^[\w.@+-]+\Z',
    #     max_length=150
    # )

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

    # def validate_email(self, email):
    #     username = self.initial_data.get('username')
    #     if CustomUser.objects.filter(username=username).first() is not None:
    #         user = CustomUser.objects.get(username=username)
    #         if user.email == email:
    #             raise serializers.ValidationError('Invalid email.')
    #         return email
    #     return email
        # if CustomUser.objects.filter(email=email).first() is not None:

    # def create(self, validated_data):
    #     username = validated_data['username']
    #     email = validated_data['email']
    #     if CustomUser.objects.get(username=username):
    #         raise serializers.ValidationError(
    #             'User with this username has been exist.')
    #     if CustomUser.objects.get(email=email):
    #         raise serializers.ValidationError(
    #             'User with this email has been exist.')
    #     user = CustomUser.objects.create(**validated_data)
    #     return user

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
