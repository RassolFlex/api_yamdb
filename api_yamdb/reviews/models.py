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

from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    bio = models.TextField('Биография', blank=True)
