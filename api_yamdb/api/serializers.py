from rest_framework import serializers

from reviews.models import Title, Genre, Category, CustomUser


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class TitleSerializer(serializers.ModelSerializer):
    # genres = serializers.SlugRelatedField()
    # category = serializers.SlugRelatedField()

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


class CustomUserSerializer(serializers.ModelSerializer):

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )

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


class CreateCustomUserSerializer(serializers.ModelSerializer):

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )
    email = serializers.EmailField(
        max_length=150,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'email',
        )


class CustomUserTokenSerializer(serializers.ModelSerializer):

    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z',
        max_length=150,
        required=True
    )
    confirmation_code = serializers.CharField(
        max_length=170,
        required=True
    )

    class Meta:
        model = CustomUser
        fields = (
            'username',
            'confirmation_code',
        )
