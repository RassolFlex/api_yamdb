import datetime
import re

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from rest_framework import serializers

from .constants import (LENGTH_FOR_FIELD,
                        LENGTH_FOR_FIELD_EMAIL,
                        LENGTH_FOR_FIELD_NAME,
                        LENGTH_FOR_FIELD_SLUG,
                        SLICE,
                        MAX_SCORE_VALUE,
                        MIN_SCORE_VALUE)


class NameSlugModel(models.Model):
    name = models.CharField(max_length=LENGTH_FOR_FIELD_NAME,
                            verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=LENGTH_FOR_FIELD_SLUG,
                            verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.slug[:SLICE]


class Title(models.Model):
    name = models.CharField(max_length=LENGTH_FOR_FIELD_NAME)
    author = models.ForeignKey(
        'ApiUser',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор'
    )
    year = models.PositiveSmallIntegerField(
        validators=[
            MaxValueValidator(datetime.date.today().year)
        ],
        verbose_name='Год',
    )
    description = models.TextField(null=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр',
        db_index=True
    )
    category = models.ForeignKey(
        'Category',
        on_delete=models.CASCADE,
        related_name='titles',
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'

    def __str__(self):
        return self.name[:SLICE]


class Genre(NameSlugModel):

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Category(NameSlugModel):

    class Meta(NameSlugModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


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
        ordering = ('username',)

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


class ReviewAndCommentBaseModel(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        ApiUser,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        abstract = True

    def __str__(self):
        return self.text[:SLICE]


class Review(ReviewAndCommentBaseModel):
    SCORE_VALIDATOR_ERROR_MESSAGE = 'Score must be in range {} - {}.'.format(
        MIN_SCORE_VALUE, MAX_SCORE_VALUE
    )

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.SmallIntegerField(
        'Оценка',
        validators=[
            MaxValueValidator(
                MAX_SCORE_VALUE,
                SCORE_VALIDATOR_ERROR_MESSAGE
            ),
            MinValueValidator(
                MIN_SCORE_VALUE,
                SCORE_VALIDATOR_ERROR_MESSAGE
            )
        ])

    class Meta(ReviewAndCommentBaseModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='only_one_review_to_title_from_user'
            )
        ]


class Comment(ReviewAndCommentBaseModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(ReviewAndCommentBaseModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        default_related_name = 'comments'
