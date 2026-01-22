import io
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from policies.models import Category, RegexRule, PolicyConfig
from alerts.models import Alert
from audit.models import AuditEvent

pytestmark = pytest.mark.django_db

def test_api_upload_and_scan_creates_alert_and_audit():
    # Configuración de políticas
    PolicyConfig.objects.create(
        risk_score_threshold=10,
        severity_threshold=3,
        store_extracted_text=False,
    )

    # Usuario
    user = User.objects.create_user(username="tester", password="1234")

    # Categoría y regla
    cat = Category.objects.create(name="Identificación")
    RegexRule.objects.create(
        name="Cedula10",
        pattern=r"\b\d{10}\b",
        category=cat,
        severity=4,
        enabled=True,
    )

    # Cliente API
    client = APIClient()
    client.login(username="tester", password="1234")

    # Archivo de prueba
    content = b"Documento de prueba\nCedula: 0912345678\n"
    file = io.BytesIO(content)
    file.name = "prueba.txt"

    response = client.post(
        "/api/documents/upload-scan/",
        data={
            "original_name": "prueba.txt",
            "file": file,
        },
        format="multipart",
    )

    assert response.status_code == 201

    data = response.json()
    assert data["scan_summary"]["findings_count"] == 1
    assert data["scan_summary"]["category"] == "Identificación"

    # Evidencia de alerta
    assert Alert.objects.count() == 1

    # Evidencia de auditoría
    assert AuditEvent.objects.filter(event_type="DOC_UPLOADED").exists()
    assert AuditEvent.objects.filter(event_type="SCAN_DONE").exists()
    assert AuditEvent.objects.filter(event_type="ALERT_CREATED").exists()
