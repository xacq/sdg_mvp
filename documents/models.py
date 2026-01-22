from django.db import models
from django.conf import settings
from policies.models import Category, RegexRule

class Document(models.Model):
    original_name = models.CharField(max_length=255)
    file = models.FileField(upload_to="docs/")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    extracted_text = models.TextField(blank=True)  # para MVP; en prod podrías no guardarlo
    classified_category = models.ForeignKey(
        Category, null=True, blank=True, on_delete=models.SET_NULL, related_name="documents"
    )
    risk_score = models.PositiveSmallIntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.id} - {self.original_name}"

class Finding(models.Model):
    """
    Hallazgos por regex
    """
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="findings")
    rule = models.ForeignKey(RegexRule, on_delete=models.PROTECT)
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    match_text = models.CharField(max_length=200)
    start_index = models.IntegerField()
    end_index = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Doc {self.document_id} - {self.rule.name}: {self.match_text}"

    class Meta:
        permissions = [
            ("view_sensitive_finding", "Puede ver coincidencias completas (sin enmascarar)"),
        ]
