from django.contrib import admin

from .models import Comment, CustomUser, Review

MODELS = [Comment, CustomUser, Review]

admin.site.register(MODELS)
