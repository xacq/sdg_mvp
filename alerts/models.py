from django.db import models
from documents.models import Document

class Alert(models.Model):
    STATUS_CHOICES = [
        ("OPEN", "Open"),
        ("ACK", "Acknowledged"),
        ("CLOSED", "Closed"),
    ]

    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name="alerts")
    title = models.CharField(max_length=200)
    severity = models.PositiveSmallIntegerField(default=3)
    details = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="OPEN")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"Alert {self.id} ({self.status})"

    class Meta:
        permissions = [
            ("ack_alert", "Puede atender/acknowledge alertas"),
        ]
