import datetime

from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

NAME_MAX_LENGTH = 256
SLUG_MAX_LENGTH = 50
NAME_SLICE_START = 0
NAME_SLICE_END = 19


class GenreCategoryModel(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Название')
    slug = models.SlugField(unique=True, max_length=SLUG_MAX_LENGTH, verbose_name='Слаг')

    class Meta:
        abstract = True
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Title(models.Model):
    name = models.CharField(max_length=NAME_MAX_LENGTH, verbose_name='Название')
    author = models.ForeignKey(
        'CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Автор'
    )
    year = models.SmallIntegerField(
        validators=[
            MinValueValidator(1000),
            MaxValueValidator(datetime.date.today().year)
        ],
        verbose_name='Год'
    )
    description = models.TextField(null=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр'
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
        return self.name[NAME_SLICE_START:NAME_SLICE_END]


class Genre(GenreCategoryModel):

    class Meta(GenreCategoryModel.Meta):
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Category(GenreCategoryModel):

    class Meta(GenreCategoryModel.Meta):
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


class CustomUser(AbstractUser):
    ROLES = (
        ('user', 'Пользователь'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    )
    username = models.CharField(
        'Логин', max_length=150, unique=True
    )
    first_name = models.CharField(
        'Имя', max_length=150, null=True, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=150, null=True, blank=True
    )
    role = models.CharField(
        'Роль', max_length=30, choices=ROLES, default='user'
    )
    email = models.EmailField(
        'email address', max_length=254, unique=True
    )
    bio = models.TextField(
        'Информация', null=True, blank=True
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username


class Review(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='reviews'
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
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.text
