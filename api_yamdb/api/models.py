from django.db import models


class Title(models.Model):
    name = models.CharField()
    year = models.DateField()
    rating = models.IntegerField()
    description = models.TextField()
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    category = models.ForeignKey('Category', on_delete=models.CASCADE)


class Genre(models.Model):
    pass


class Category(models.Model):
    pass
