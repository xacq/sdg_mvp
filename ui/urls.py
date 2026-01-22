from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("login/", auth_views.LoginView.as_view(
        template_name="ui/login.html"
    ), name="login"),

    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    path("", views.dashboard, name="dashboard"),
    path("documents/", views.documents_list, name="documents_list"),
    path("documents/<int:doc_id>/", views.document_detail, name="document_detail"),
    path("alerts/", views.alerts_list, name="alerts_list"),
    path("audit/", views.audit_list, name="audit_list"),
    path("upload/", views.document_upload, name="document_upload"),

    path("alerts/<int:alert_id>/ack/", views.alert_acknowledge, name="alert_ack"),

    path("alerts/<int:alert_id>/close/", views.alert_close, name="alert_close"),
    path("alerts/<int:alert_id>/reopen/", views.alert_reopen, name="alert_reopen"),

]
