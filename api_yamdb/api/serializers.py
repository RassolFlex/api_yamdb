from statistics import mean

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
