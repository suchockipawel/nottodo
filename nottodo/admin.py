from django.contrib import admin
from .models import NotToDo, SharedNotToDo, Comment, EmailLog

@admin.register(NotToDo)
class NotToDoAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'context', 'scheduled_start_time', 'repeat', 'created_at', 'updated_at')

@admin.register(SharedNotToDo)
class SharedNotToDoAdmin(admin.ModelAdmin):
    list_display = ('nottodo', 'shared_with', 'created_at')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('shared_nottodo', 'user', 'text', 'created_at')

@admin.register(EmailLog)
class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('nottodo', 'user', 'email', 'subject', 'sent_at', 'success', 'error_message')
    list_filter = ('sent_at', 'success')
    search_fields = ('email', 'subject', 'error_message')
