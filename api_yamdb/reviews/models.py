from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Title(models.Model):
    name = models.CharField(max_length=28)
    year = models.DateField()  # Предполагаю должен быть интегер
    rating = models.IntegerField()
    description = models.TextField()
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, max_length=16)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=16)
    slug = models.SlugField(unique=True, max_length=16)

    def __str__(self):
        return self.name


class CustomUser(AbstractUser):
    bio = models.TextField('Биография', blank=True)


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

    def __str__(self):
        return self.name


class Comment(models.Model):
    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='comments'
    )
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments'
    )
    text = models.TextField()
    author = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='comments'
    )
    pub_date = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.name
