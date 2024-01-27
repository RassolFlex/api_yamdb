from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import ApiUser
from .constants import LIST_PER_PAGE


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
