# audit/urls.py
from django.urls import path
from .views import AuditListView

urlpatterns = [
    path("", AuditListView.as_view()),
]
