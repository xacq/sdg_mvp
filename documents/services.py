import re
from dataclasses import dataclass
from typing import List, Optional, Tuple

from django.db import transaction
from django.utils import timezone

from policies.models import RegexRule, Category
from .models import Document, Finding
from alerts.models import Alert
from audit.models import AuditEvent

from docx import Document as DocxDocument
from pdfminer.high_level import extract_text as pdf_extract_text
from policies.models import PolicyConfig


@dataclass
class ScanResult:
    category: Optional[Category]
    risk_score: int
    findings_count: int
    max_severity: int

def _extract_text_from_file(path: str, filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    if lower.endswith(".docx"):
        doc = DocxDocument(path)
        return "\n".join(p.text for p in doc.paragraphs)

    if lower.endswith(".pdf"):
        # pdfminer ya devuelve texto "extraído"
        return pdf_extract_text(path) or ""

    # fallback
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8", errors="ignore")

def _normalize_text(text: str) -> str:
    # Normalización simple MVP
    return text.replace("\r\n", "\n").replace("\r", "\n")

def _find_matches(pattern: str, text: str) -> List[Tuple[str, int, int]]:
    matches = []
    for m in re.finditer(pattern, text, flags=re.IGNORECASE | re.MULTILINE):
        snippet = m.group(0)
        start, end = m.start(), m.end()
        # Evitar hallazgos gigantes
        snippet = snippet[:200]
        matches.append((snippet, start, end))
    return matches

@transaction.atomic
def scan_and_classify_document(doc: Document, actor_id: int) -> ScanResult:
    # 0) Cargar configuración (RF-03 / RNF seguridad)
    config = PolicyConfig.objects.first()
    risk_threshold = config.risk_score_threshold if config else 20
    severity_threshold = config.severity_threshold if config else 4
    store_text = config.store_extracted_text if config else False

    # 1) Extraer texto
    path = doc.file.path
    text = _normalize_text(_extract_text_from_file(path, doc.original_name))

    # Guardar o no guardar texto (seguridad)
    doc.extracted_text = text if store_text else ""

    AuditEvent.objects.create(
        event_type="TEXT_EXTRACTED",
        actor_id=actor_id,
        object_type="Document",
        object_id=str(doc.id),
        message="Texto extraído para análisis",
        meta_json={"chars": len(text)},
        created_at=timezone.now(),
    )

    # 2) Cargar reglas
    rules = RegexRule.objects.select_related("category").filter(enabled=True).all()

    findings_created = 0
    max_sev = 0
    sev_sum = 0
    category_counts = {}

    # 3) Ejecutar regex y registrar hallazgos
    for rule in rules:
        found = _find_matches(rule.pattern, text)
        if not found:
            continue

        for snippet, start, end in found:
            Finding.objects.create(
                document=doc,
                rule=rule,
                category=rule.category,
                match_text=snippet,
                start_index=start,
                end_index=end,
            )
            findings_created += 1

        max_sev = max(max_sev, rule.severity)
        sev_sum += rule.severity * len(found)
        category_counts[rule.category_id] = category_counts.get(rule.category_id, 0) + len(found)

    # 4) Clasificar categoría
    chosen_category = None
    if category_counts:
        top_cat_id = max(category_counts.items(), key=lambda x: x[1])[0]
        chosen_category = Category.objects.get(id=top_cat_id)

    # 5) Risk score
    risk_score = min(100, sev_sum)

    doc.classified_category = chosen_category
    doc.risk_score = risk_score
    doc.save(update_fields=["extracted_text", "classified_category", "risk_score"])

    AuditEvent.objects.create(
        event_type="SCAN_DONE",
        actor_id=actor_id,
        object_type="Document",
        object_id=str(doc.id),
        message="Escaneo regex finalizado",
        meta_json={
            "findings": findings_created,
            "max_severity": max_sev,
            "risk_score": risk_score,
            "category": chosen_category.name if chosen_category else None,
        },
        created_at=timezone.now(),
    )

    # 6) Alertas (RF-04) según umbrales configurables
    if findings_created > 0 and (
        max_sev >= severity_threshold or risk_score >= risk_threshold
    ):
        alert = Alert.objects.create(
            document=doc,
            title="Detección de contenido sensible",
            severity=max_sev if max_sev else 3,
            details=(
                f"Hallazgos: {findings_created}. Riesgo: {risk_score}. "
                f"Categoría: {chosen_category.name if chosen_category else 'N/A'}"
            ),
        )
        AuditEvent.objects.create(
            event_type="ALERT_CREATED",
            actor_id=actor_id,
            object_type="Alert",
            object_id=str(alert.id),
            message="Alerta creada por detección",
            meta_json={"document_id": doc.id},
            created_at=timezone.now(),
        )

    return ScanResult(
        category=chosen_category,
        risk_score=risk_score,
        findings_count=findings_created,
        max_severity=max_sev,
    )
