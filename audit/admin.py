from django.contrib import admin
from .models import AuditEvent

@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "event_type", "actor", "object_type", "object_id")
    list_filter = ("event_type", "created_at")
    search_fields = ("message", "object_id")
