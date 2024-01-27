import re

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework import serializers

from .constants import (LENGTH_FOR_FIELD,
                        LENGTH_FOR_FIELD_EMAIL,
                        LENGTH_FOR_FIELD_NAME,
                        LENGTH_FOR_FIELD_SLUG,
                        SLICE)


class Title(models.Model):
    name = models.CharField(max_length=LENGTH_FOR_FIELD_NAME)
    author = models.ForeignKey(
        'ApiUser',
        on_delete=models.SET_NULL,
        null=True
    )
    year = models.IntegerField()
    description = models.TextField(null=True)
    genre = models.ManyToManyField('Genre', through='GenreTitle')
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='titles'
    )

    def __str__(self):
        return self.name[:SLICE]


class Genre(models.Model):
    name = models.CharField(max_length=LENGTH_FOR_FIELD_NAME)
    slug = models.SlugField(unique=True, max_length=LENGTH_FOR_FIELD_SLUG)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug[:SLICE]


class Category(models.Model):
    name = models.CharField(max_length=LENGTH_FOR_FIELD_NAME)
    slug = models.SlugField(unique=True, max_length=LENGTH_FOR_FIELD_SLUG)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug[:SLICE]


class ApiUser(AbstractUser):

    class UserRoles(models.TextChoices):
        USER = 'user', 'Пользователь'
        MODERATOR = 'moderator', 'Модератор'
        ADMIN = 'admin', 'Администратор'

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    username = models.CharField(
        'Логин', max_length=LENGTH_FOR_FIELD, unique=True
    )
    first_name = models.CharField(
        'Имя', max_length=LENGTH_FOR_FIELD, null=True, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=LENGTH_FOR_FIELD, null=True, blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=max((len(role[0]) for role in UserRoles.choices)),
        choices=UserRoles.choices,
        default=UserRoles.USER,
    )
    email = models.EmailField(
        'email address', max_length=LENGTH_FOR_FIELD_EMAIL, unique=True
    )
    bio = models.TextField(
        'Информация', null=True, blank=True
    )

    class Meta():
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'

    def check_username(username):
        if not username:
            raise serializers.ValidationError('Username must be not empty.')
        if len(username) > LENGTH_FOR_FIELD:
            raise serializers.ValidationError('Username over 150 length.')
        if username == 'me':
            raise serializers.ValidationError(
                'Username should not be equal "me".')
        pattern = r'^[\w.@+-]+\Z'
        if not re.match(pattern, username):
            raise serializers.ValidationError('Invalid username.')
        return username

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username[:SLICE]


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        ApiUser, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='only_one_review_to_title_from_user'
            )
        ]

    def __str__(self):
        return self.text[:SLICE]


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        ApiUser, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.text[:SLICE]


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
