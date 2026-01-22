from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

from documents.models import Document, Finding
from alerts.models import Alert
from audit.models import AuditEvent
from policies.models import Category, RegexRule, PolicyConfig

class Command(BaseCommand):
    help = "Crea roles (Administrador, Responsable de Seguridad, Usuario Técnico) y asigna permisos"

    def handle(self, *args, **options):
        admin_g, _ = Group.objects.get_or_create(name="Administrador")
        sec_g, _ = Group.objects.get_or_create(name="Responsable de Seguridad")
        tech_g, _ = Group.objects.get_or_create(name="Usuario Técnico")

        def perms_for_model(model):
            ct = ContentType.objects.get_for_model(model)
            return Permission.objects.filter(content_type=ct)

        # Permisos base por modelo (view/add/change/delete)
        doc_perms = perms_for_model(Document)
        finding_perms = perms_for_model(Finding)
        alert_perms = perms_for_model(Alert)
        audit_perms = perms_for_model(AuditEvent)
        cat_perms = perms_for_model(Category)
        rule_perms = perms_for_model(RegexRule)
        cfg_perms = perms_for_model(PolicyConfig)

        # Permisos custom
        ack_perm = Permission.objects.get(codename="ack_alert")
        sensitive_perm = Permission.objects.get(codename="view_sensitive_finding")

        # Administrador: todo
        admin_g.permissions.set(
            list(doc_perms) + list(finding_perms) + list(alert_perms) + list(audit_perms)
            + list(cat_perms) + list(rule_perms) + list(cfg_perms)
            + [ack_perm, sensitive_perm]
        )

        # Responsable Seguridad:
        # - ver docs/hallazgos completos
        # - ver alertas + atender
        # - ver auditoría
        sec_g.permissions.set(
            [
                Permission.objects.get(codename="view_document"),
                Permission.objects.get(codename="view_finding"),
                Permission.objects.get(codename="view_alert"),
                Permission.objects.get(codename="change_alert"),
                Permission.objects.get(codename="view_auditevent"),
                ack_perm,
                sensitive_perm,
            ]
        )

        # Usuario Técnico:
        # - cargar docs
        # - ver docs
        # - NO ver auditoría global
        # - NO atender alertas
        tech_g.permissions.set(
            [
                Permission.objects.get(codename="add_document"),
                Permission.objects.get(codename="view_document"),
                Permission.objects.get(codename="view_alert"),
            ]
        )

        self.stdout.write(self.style.SUCCESS("Roles creados y permisos asignados."))
