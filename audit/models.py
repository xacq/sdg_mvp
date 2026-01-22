from django.db import models
from django.conf import settings

class AuditEvent(models.Model):
    event_type = models.CharField(max_length=80)  # e.g., DOC_UPLOADED, SCAN_DONE, ALERT_CREATED
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    object_type = models.CharField(max_length=80, blank=True)
    object_id = models.CharField(max_length=80, blank=True)
    message = models.TextField(blank=True)
    meta_json = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.created_at} {self.event_type}"
