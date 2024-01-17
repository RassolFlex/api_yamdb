from django.contrib.auth.models import AbstractUser
from django.db import models


class Title(models.Model):
    name = models.CharField(max_length=28)
    year = models.DateField()
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
