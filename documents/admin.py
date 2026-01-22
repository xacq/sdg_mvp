from django.contrib import admin
from .models import Document, Finding

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "original_name", "uploaded_by", "uploaded_at", "classified_category", "risk_score")
    list_filter = ("classified_category", "uploaded_at")
    search_fields = ("original_name",)

@admin.register(Finding)
class FindingAdmin(admin.ModelAdmin):
    list_display = ("document", "rule", "category", "match_text", "created_at")
    list_filter = ("category", "rule")
    search_fields = ("match_text",)
