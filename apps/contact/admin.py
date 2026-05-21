from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email','phone', 'short_message','is_sent', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone', 'message')
    list_filter = ('created_at',)
    readonly_fields = ('first_name', 'last_name', 'email', 'phone', 'message', 'created_at')
    ordering = ('-created_at',)

    def short_message(self, obj):
        return obj.message[:40] + '...' if len(obj.message) > 40 else obj.message

    short_message.short_description = "Message"
