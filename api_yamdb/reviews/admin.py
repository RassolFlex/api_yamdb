from django.contrib import admin

from .models import CustomUser, Title, Category, Genre

admin.site.register(CustomUser)

@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'year',
        'description',
        'category',
    ]
    list_editable = [
        'author',
        'year',
        'description',
        'category',
    ]
    list_filter = [
        'author',
        'year',
        'genre',
        'category',
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    pass
