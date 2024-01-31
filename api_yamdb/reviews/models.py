from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .constants import (LENGTH_FOR_FIELD,
                        LENGTH_FOR_FIELD_EMAIL,
                        LENGTH_FOR_FIELD_NAME,
                        LENGTH_FOR_FIELD_SLUG,
                        SCORE_VALIDATOR_ERROR_MESSAGE,
                        SLICE,
                        MAX_SCORE_VALUE,
                        MIN_SCORE_VALUE)
from .validators import check_username, year_validator


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
    year = models.SmallIntegerField(
        validators=(
            year_validator,
        ),
        verbose_name='Год',
        db_index=True
    )
    description = models.TextField(null=True, verbose_name='Описание')
    genre = models.ManyToManyField(
        'Genre',
        verbose_name='Жанр',
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
    REQUIRED_FIELDS = ('username',)

    username = models.CharField(
        'Логин', max_length=LENGTH_FOR_FIELD, unique=True,
        validators=(check_username,)
    )
    first_name = models.CharField(
        'Имя', max_length=LENGTH_FOR_FIELD, null=True, blank=True
    )
    last_name = models.CharField(
        'Фамилия', max_length=LENGTH_FOR_FIELD, null=True, blank=True
    )
    role = models.CharField(
        'Роль',
        max_length=max(len(role) for role, _ in UserRoles.choices),
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

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser or self.is_staff

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    def __str__(self):
        return self.username[:SLICE]


class TextAuthorPubDateBaseModel(models.Model):
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


class Review(TextAuthorPubDateBaseModel):

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        'Оценка',
        validators=(
            MaxValueValidator(
                MAX_SCORE_VALUE,
                SCORE_VALIDATOR_ERROR_MESSAGE
            ),
            MinValueValidator(
                MIN_SCORE_VALUE,
                SCORE_VALIDATOR_ERROR_MESSAGE
            )
        ))

    class Meta(TextAuthorPubDateBaseModel.Meta):
        verbose_name = 'отзыв'
        verbose_name_plural = 'отзывы'
        default_related_name = 'reviews'
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='only_one_review_to_title_from_user'
            ),
        )


class Comment(TextAuthorPubDateBaseModel):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )

    class Meta(TextAuthorPubDateBaseModel.Meta):
        verbose_name = 'комментарий'
        verbose_name_plural = 'комментарии'
        default_related_name = 'comments'
