from rest_framework import serializers

from reviews.models import Title, Genre, Category


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name',)


class TitleSerializer(serializers.ModelSerializer):
    genres = serializers.SlugRelatedField()
    category = serializers.SlugRelatedField()

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
