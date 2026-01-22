from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Count

from documents.models import Document
from alerts.models import Alert
from audit.models import AuditEvent

from django.db.models import Exists, OuterRef
from documents.models import Document, Finding

from django.contrib import messages
from django.shortcuts import redirect
from ui.forms import DocumentUploadForm

from documents.models import Document
from documents.services import scan_and_classify_document
from audit.models import AuditEvent

from django.views.decorators.http import require_POST
from django.db.models import Q
from django.core.exceptions import PermissionDenied


@login_required
def dashboard(request):
    total_documents = Document.objects.count()
    documents_with_alerts = Document.objects.filter(alerts__isnull=False).distinct().count()
    open_alerts = Alert.objects.filter(status="OPEN").count()
    open_sev5 = Alert.objects.filter(status="OPEN", severity=5).count()
    open_sev4 = Alert.objects.filter(status="OPEN", severity=4).count()
    open_sev3 = Alert.objects.filter(status="OPEN", severity=3).count()

    latest_documents = (
        Document.objects
        .select_related("classified_category")
        .order_by("-uploaded_at")[:5]
    )

    latest_events = (
        AuditEvent.objects
        .select_related("actor")
        .order_by("-created_at")[:10]
    )

    context = {
        "total_documents": total_documents,
        "documents_with_alerts": documents_with_alerts,
        "open_alerts": open_alerts,
        "latest_documents": latest_documents,
        "latest_events": latest_events,
        "open_sev5": open_sev5,
        "open_sev4": open_sev4,
        "open_sev3": open_sev3,
    }

    return render(request, "ui/dashboard.html", context)


@login_required
def documents_list(request):
    # Anotación para saber si tiene alertas sin hacer N+1
    alert_exists = Alert.objects.filter(document_id=OuterRef("pk"))
    docs = (
        Document.objects
        .select_related("classified_category", "uploaded_by")
        .annotate(has_alert=Exists(alert_exists))
        .order_by("-uploaded_at")
    )

    context = {"documents": docs}
    return render(request, "ui/documents_list.html", context)


from django.shortcuts import get_object_or_404

@login_required
def document_detail(request, doc_id: int):
    doc = get_object_or_404(
        Document.objects.select_related("classified_category", "uploaded_by"),
        id=doc_id
    )

    findings = (
        doc.findings
        .select_related("rule", "category")
        .order_by("-created_at")
    )

    alerts = (
        doc.alerts
        .order_by("-created_at")
    )

    events = (
        AuditEvent.objects
        .filter(object_type="Document", object_id=str(doc.id))
        .select_related("actor")
        .order_by("-created_at")[:30]
    )

    context = {
        "doc": doc,
        "findings": findings,
        "alerts": alerts,
        "events": events,
    }
    return render(request, "ui/document_detail.html", context)




@login_required
def alerts_list(request):
    # Permiso mínimo para ver alertas
    if not request.user.has_perm("alerts.view_alert"):
        raise PermissionDenied

    status = request.GET.get("status", "OPEN")  # OPEN por defecto
    severity = request.GET.get("severity", "")
    q = request.GET.get("q", "").strip()

    alerts = Alert.objects.select_related("document").order_by("-created_at")

    if status:
        alerts = alerts.filter(status=status)

    if severity.isdigit():
        alerts = alerts.filter(severity=int(severity))

    if q:
        # buscar por nombre de documento o por id
        alerts = alerts.filter(
            Q(document__original_name__icontains=q) |
            Q(document__id__icontains=q)
        )

    context = {
        "alerts": alerts[:200],  # límite razonable en UI
        "status": status,
        "severity": severity,
        "q": q,
    }
    return render(request, "ui/alerts_list.html", context)


from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.utils.dateparse import parse_datetime

@login_required
def audit_list(request):
    if not request.user.has_perm("audit.view_auditevent"):
        raise PermissionDenied

    event_type = request.GET.get("event_type", "").strip()
    actor = request.GET.get("actor", "").strip()
    date_from = request.GET.get("from", "").strip()
    date_to = request.GET.get("to", "").strip()
    q = request.GET.get("q", "").strip()

    events = (
        AuditEvent.objects
        .select_related("actor")
        .order_by("-created_at")
    )

    if event_type:
        events = events.filter(event_type=event_type)

    if actor:
        # username exact o contiene
        events = events.filter(actor__username__icontains=actor)

    # Fechas: esperamos "YYYY-MM-DD" o "YYYY-MM-DDTHH:MM"
    # Para simplificar UI, usamos date (YYYY-MM-DD) y convertimos a rango.
    if date_from:
        # 00:00 del día
        events = events.filter(created_at__date__gte=date_from)

    if date_to:
        # 23:59 del día
        events = events.filter(created_at__date__lte=date_to)

    if q:
        events = events.filter(
            Q(message__icontains=q) |
            Q(object_id__icontains=q) |
            Q(object_type__icontains=q)
        )

    # Para el dropdown de tipos (solo los existentes)
    event_types = (
        AuditEvent.objects
        .values_list("event_type", flat=True)
        .distinct()
        .order_by("event_type")
    )

    context = {
        "events": events[:300],  # límite para UI
        "event_types": event_types,
        "event_type": event_type,
        "actor": actor,
        "date_from": date_from,
        "date_to": date_to,
        "q": q,
    }
    return render(request, "ui/audit_list.html", context)


@login_required
def document_upload(request):
    if request.method == "POST":
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            original_name = form.cleaned_data["original_name"]
            uploaded_file = form.cleaned_data["file"]

            # 1) Crear documento
            doc = Document.objects.create(
                original_name=original_name,
                file=uploaded_file,
                uploaded_by=request.user,
            )

            # 2) Auditar carga
            AuditEvent.objects.create(
                event_type="DOC_UPLOADED",
                actor=request.user,
                object_type="Document",
                object_id=str(doc.id),
                message="Documento cargado desde la interfaz UI",
                meta_json={"name": doc.original_name},
            )

            # 3) Escanear y clasificar (servicio interno)
            scan_and_classify_document(doc=doc, actor_id=request.user.id)

            messages.success(request, "Documento cargado y escaneado correctamente.")
            return redirect("document_detail", doc_id=doc.id)

        messages.error(request, "Revisa el formulario. Hay errores.")
    else:
        form = DocumentUploadForm()

    return render(request, "ui/upload.html", {"form": form})


@login_required
@require_POST
def alert_acknowledge(request, alert_id: int):
    if not request.user.has_perm("alerts.ack_alert"):
        raise PermissionDenied

    alert = get_object_or_404(Alert, id=alert_id)
    alert.status = "ACK"
    alert.save(update_fields=["status"])

    AuditEvent.objects.create(
        event_type="ALERT_ACK",
        actor=request.user,
        object_type="Alert",
        object_id=str(alert.id),
        message="Alerta marcada como atendida desde UI",
        meta_json={"document_id": alert.document_id},
    )

    messages.success(request, "Alerta marcada como atendida.")
    return redirect("document_detail", doc_id=alert.document_id)


@login_required
@require_POST
def alert_close(request, alert_id: int):
    if not request.user.has_perm("alerts.change_alert"):
        raise PermissionDenied

    alert = get_object_or_404(Alert, id=alert_id)
    alert.status = "CLOSED"
    alert.save(update_fields=["status"])

    AuditEvent.objects.create(
        event_type="ALERT_CLOSED",
        actor=request.user,
        object_type="Alert",
        object_id=str(alert.id),
        message="Alerta cerrada desde UI",
        meta_json={"document_id": alert.document_id},
    )

    messages.success(request, "Alerta cerrada.")
    return redirect("alerts_list")


@login_required
@require_POST
def alert_reopen(request, alert_id: int):
    if not request.user.has_perm("alerts.change_alert"):
        raise PermissionDenied

    alert = get_object_or_404(Alert, id=alert_id)
    alert.status = "OPEN"
    alert.save(update_fields=["status"])

    AuditEvent.objects.create(
        event_type="ALERT_REOPENED",
        actor=request.user,
        object_type="Alert",
        object_id=str(alert.id),
        message="Alerta reabierta desde UI",
        meta_json={"document_id": alert.document_id},
    )

    messages.success(request, "Alerta reabierta.")
    return redirect("alerts_list")

