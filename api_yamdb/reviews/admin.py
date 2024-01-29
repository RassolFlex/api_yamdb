from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .constants import LIST_PER_PAGE
from .models import ApiUser, Category, Comment, Genre, Review, Title


class ReviewAndCommentBaseAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'pub_date'
    )
    list_display_links = ('text',)
    search_fields = ('author', 'text', 'pub_date')
    empty_value_display = 'Не указано'


@admin.register(Review)
class ReviewAdmin(ReviewAndCommentBaseAdmin):

    def get_list_display(self, request):
        return self.list_display + ('title',)

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ('title',)


@admin.register(Comment)
class CommentAdmin(ReviewAndCommentBaseAdmin):

    def get_list_display(self, request):
        return self.list_display + ('review',)

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ('review',)


@admin.register(ApiUser)
class ApiUserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'bio',
        'is_superuser',
        'is_staff',
    )
    list_editable = (
        'first_name',
        'last_name',
        'role',
        'bio',
        'is_superuser',
        'is_staff',
    )
    search_fields = ('username', 'email', 'role', 'first_name', 'last_name',)
    list_filter = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'is_superuser',
        'is_staff',
    )
    list_display_links = ('username', 'email',)
    list_per_page = LIST_PER_PAGE
    empty_value_display = 'Не указано'


class GenreCategoryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'slug',
    )
    list_editable = (
        'slug',
    )
    list_filter = (
        'name',
    )
    search_fields = ('name',)
    list_per_page = LIST_PER_PAGE
    empty_value_display = 'Не указано'


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'year',
        'category',
        'get_genre',
        'description',
    )
    list_editable = (
        'author',
        'year',
        'description',
        'category',
    )
    list_filter = (
        'author',
        'year',
        'genre',
        'category',
    )
    search_fields = (
        'name',
        'author__username',
        'genre__name',
        'category__name',
        'year'
    )
    list_per_page = LIST_PER_PAGE
    empty_value_display = 'Не указано'

    @admin.display(description='Жанр')
    def get_genre(self, obj):
        return ' ,'.join([genre.slug for genre in obj.genre.all()])


@admin.register(Genre)
class GenreAdmin(GenreCategoryAdmin):
    pass


@admin.register(Category)
class CategoryAdmin(GenreCategoryAdmin):
    pass
