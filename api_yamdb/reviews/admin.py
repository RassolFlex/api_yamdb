from django.contrib import admin

from .models import Comment, CustomUser, Review


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
