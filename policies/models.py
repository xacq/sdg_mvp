from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.name

class RegexRule(models.Model):
    """
    Regla de detección (RF-01) + mapeo a categoría (RF-02)
    """
    name = models.CharField(max_length=150, unique=True)
    pattern = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="rules")
    enabled = models.BooleanField(default=True)

    # severidad/impacto de 1-5, para disparar alertas
    severity = models.PositiveSmallIntegerField(default=3)

    def __str__(self) -> str:
        return f"{self.name} (sev={self.severity})"

class PolicyConfig(models.Model):
    """
    Configuración global del motor de políticas (1 sola fila).
    """
    risk_score_threshold = models.PositiveSmallIntegerField(default=20)
    severity_threshold = models.PositiveSmallIntegerField(default=4)
    store_extracted_text = models.BooleanField(
        default=False,
        help_text="Si es False, no se almacena el texto extraído (seguridad)"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Configuración Global de Políticas"

    class Meta:
        verbose_name = "Configuración de Política"
        verbose_name_plural = "Configuración de Políticas"
