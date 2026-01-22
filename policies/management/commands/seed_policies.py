from django.core.management.base import BaseCommand
from policies.models import Category, RegexRule

class Command(BaseCommand):
    help = "Crea categorías y reglas regex de ejemplo"

    def handle(self, *args, **options):
        cat_id, _ = Category.objects.get_or_create(name="Identificación", defaults={"description": "Cédula/RUC"})
        cat_fin, _ = Category.objects.get_or_create(name="Financiero", defaults={"description": "Tarjetas y cuentas"})

        # Ecuador (muy simplificado para MVP)
        RegexRule.objects.get_or_create(
            name="Cédula EC (10 dígitos)",
            defaults={
                "pattern": r"\b\d{10}\b",
                "category": cat_id,
                "severity": 4,
                "enabled": True,
            },
        )

        RegexRule.objects.get_or_create(
            name="RUC EC (13 dígitos)",
            defaults={
                "pattern": r"\b\d{13}\b",
                "category": cat_id,
                "severity": 4,
                "enabled": True,
            },
        )

        # Tarjeta (Luhn NO aplicado; MVP regex)
        RegexRule.objects.get_or_create(
            name="Posible tarjeta (13-19 dígitos)",
            defaults={
                "pattern": r"\b\d{13,19}\b",
                "category": cat_fin,
                "severity": 5,
                "enabled": True,
            },
        )

        self.stdout.write(self.style.SUCCESS("Seed completado."))
