from statistics import mean

from rest_framework import serializers

from reviews.models import Category, CustomUser, Genre, Title


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)

    def validate(self, attrs):
        if len(attrs['slug']) > 50:
            raise serializers.ValidationError(
                'Max 50 characters allowed'
            )
        return attrs


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(read_only=True, slug_field='slug')
    category = serializers.SlugRelatedField(read_only=True, slug_field='slug')
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
            return 'None'
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
