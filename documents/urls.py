from django.urls import path
from .views import DocumentUploadAndScanView, DocumentDetailView

urlpatterns = [
    path("upload-scan/", DocumentUploadAndScanView.as_view()),
    path("<int:doc_id>/", DocumentDetailView.as_view()),
]
