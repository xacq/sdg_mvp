from django.contrib import admin
from .models import Category, RegexRule, PolicyConfig

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)

@admin.register(RegexRule)
class RegexRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "enabled", "severity")
    list_filter = ("enabled", "category", "severity")
    search_fields = ("name", "pattern")

@admin.register(PolicyConfig)
class PolicyConfigAdmin(admin.ModelAdmin):
    list_display = (
        "risk_score_threshold",
        "severity_threshold",
        "store_extracted_text",
        "updated_at",
    )

    def has_add_permission(self, request):
        # Solo permitir una fila
        return not PolicyConfig.objects.exists()

