from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Title(models.Model):
    name = models.CharField(max_length=28)
    author = models.ForeignKey(
        'CustomUser',
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
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.slug


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


class ReviewAndCommentBaseModel(models.Model):
    text = models.TextField('Текст отзыва')
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE  # related_name='reviews'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        abstract = True


class Review(ReviewAndCommentBaseModel):
    SCORE_VALIDATOR_ERROR_MESSAGE = 'Score must be in range 1 - 10.'

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.SmallIntegerField(
        'Оценка',
        validators=[
            MaxValueValidator(10, SCORE_VALIDATOR_ERROR_MESSAGE),
            MinValueValidator(1, SCORE_VALIDATOR_ERROR_MESSAGE)
        ])

    class Meta(ReviewAndCommentBaseModel.Meta):
        verbose_name = "отзыв"
        verbose_name_plural = "отзывы"
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='only_one_review_to_title_from_user'
            )
        ]

    def __str__(self):
        return self.text


class Comment(ReviewAndCommentBaseModel):
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )

    class Meta(ReviewAndCommentBaseModel.Meta):
        verbose_name = "комментарий"
        verbose_name_plural = "комментарии"

    def __str__(self):
        return self.text


class GenreTitle(models.Model):
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
