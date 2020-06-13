from django.contrib import admin
from .models import Comment

@admin.register(Comment)
class Comment(admin.ModelAdmin):
    list_display = ('id', 'content_object', 'text', 'comment_time', 'user')
