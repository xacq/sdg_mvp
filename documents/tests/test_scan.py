import io
import pytest
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile

from policies.models import Category, RegexRule
from documents.models import Document
from documents.services import scan_and_classify_document
from alerts.models import Alert
from audit.models import AuditEvent

pytestmark = pytest.mark.django_db

def test_scan_creates_findings_alert_and_audit(tmp_path):
    user = User.objects.create_user(username="u1", password="pass")

    cat = Category.objects.create(name="Identificación")
    RegexRule.objects.create(
        name="Cedula10",
        pattern=r"\b\d{10}\b",
        category=cat,
        severity=4,
        enabled=True,
    )

    content = b"Hola\nCedula: 0912345678\n"
    upload = SimpleUploadedFile("prueba.txt", content, content_type="text/plain")

    doc = Document.objects.create(
        original_name="prueba.txt",
        file=upload,
        uploaded_by=user,
    )

    result = scan_and_classify_document(doc=doc, actor_id=user.id)

    doc.refresh_from_db()
    assert result.findings_count == 1
    assert doc.classified_category.name == "Identificación"
    assert doc.risk_score > 0

    assert Alert.objects.filter(document=doc).count() == 1
    assert AuditEvent.objects.filter(object_id=str(doc.id), event_type="SCAN_DONE").exists()
