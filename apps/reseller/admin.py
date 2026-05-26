from django.contrib import admin
from .models import ResellerApplication

@admin.register(ResellerApplication)
class ResellerApplicationAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'contact_name', 'email', 'phone', 'country', 'signature_date', 'is_sent', 'created_at')
    search_fields = ('company_name', 'contact_name', 'email', 'phone', 'city', 'country', 'full_name')
    list_filter = ('is_sent', 'created_at', 'signature_date')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)
