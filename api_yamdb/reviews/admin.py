from django.contrib import admin

from .models import CustomUser, Title, Category, Genre

admin.site.register(CustomUser)


class GenreCategoryAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'slug'
    ]
    list_editable = [
        'slug'
    ]
    list_filter = [
        'name',
    ]
    search_fields = ['name']


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = [
        'name',
        'author',
        'year',
        'category',
        'get_genre',
        'description',
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
    search_fields = [
        'name',
        'author__username',
        'genre__name',
        'category__name',
        'year'
    ]

    def get_genre(self, obj):
        return '\n'.join([i.slug for i in obj.genre.all()])


@admin.register(Genre)
class GenreAdmin(GenreCategoryAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(GenreCategoryAdmin):
    pass
