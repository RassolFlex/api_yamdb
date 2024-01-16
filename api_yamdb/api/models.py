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
    pass


class Category(models.Model):
    pass
