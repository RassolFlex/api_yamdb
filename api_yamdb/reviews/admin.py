from django.contrib import admin

from .models import Comment, CustomUser, Review, Title, Category, Genre


class ReviewAndCommentBaseAdmin(admin.ModelAdmin):
    list_display = (
        'text',
        'author',
        'pub_date'
    )
    list_display_links = ('text',)
    search_fields = ('author', 'text', 'pub_date')
    empty_value_display = '-пусто-'


class ReviewAdmin(ReviewAndCommentBaseAdmin):

    def get_list_display(self, request):
        return self.list_display + ('title',)

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ('title',)


class CommentAdmin(ReviewAndCommentBaseAdmin):

    def get_list_display(self, request):
        return self.list_display + ('review',)

    def get_list_display_links(self, request, list_display):
        return self.list_display_links + ('review',)


admin.site.register(Comment, CommentAdmin)
admin.site.register(Review, ReviewAdmin)
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
