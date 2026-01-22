from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("ui.urls")),
    path("api/documents/", include("documents.urls")),
    path("api/policies/", include("policies.urls")),
    path("api/alerts/", include("alerts.urls")),
    path("api/audit/", include("audit.urls")),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
