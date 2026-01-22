from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser

from audit.models import AuditEvent
from .serializers import DocumentUploadSerializer, DocumentDetailSerializer
from .services import scan_and_classify_document

class DocumentUploadAndScanView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]  # <-- CLAVE para archivos

    def get(self, request):
        """
        Solo para que la interfaz navegable de DRF muestre el formulario.
        """
        ser = DocumentUploadSerializer()
        return Response({
            "hint": "Usa POST multipart/form-data con: original_name (str) y file (archivo).",
            "fields": list(ser.fields.keys()),
        })

    def post(self, request):
        ser = DocumentUploadSerializer(data=request.data, context={"request": request})
        ser.is_valid(raise_exception=True)
        doc = ser.save()

        AuditEvent.objects.create(
            event_type="DOC_UPLOADED",
            actor=request.user,
            object_type="Document",
            object_id=str(doc.id),
            message="Documento cargado",
            meta_json={"name": doc.original_name},
        )

        result = scan_and_classify_document(doc=doc, actor_id=request.user.id)

        detail = DocumentDetailSerializer(doc)
        return Response(
            {
                "document": detail.data,
                "scan_summary": {
                    "risk_score": result.risk_score,
                    "findings_count": result.findings_count,
                    "max_severity": result.max_severity,
                    "category": result.category.name if result.category else None,
                },
            },
            status=status.HTTP_201_CREATED,
        )

class DocumentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, doc_id: int):
        doc = Document.objects.prefetch_related("findings__rule", "findings__category").get(id=doc_id)
        return Response(DocumentDetailSerializer(doc).data)
