from django.conf import settings
from django.db import models

from catalog.models.base import TimestampedModel


class Empresa(TimestampedModel):
    """
    Tenant do sistema: cada empresa (lojista com CNPJ) tem seu próprio
    catálogo e financeiro. Todo dado de negócio é escopado por este modelo.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empresa",
        verbose_name="usuário responsável",
    )
    nome = models.CharField(max_length=255, verbose_name="nome da empresa")
    cnpj = models.CharField(
        max_length=14,
        unique=True,
        verbose_name="CNPJ",
        help_text="Somente dígitos (14).",
    )

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["nome"]

    def __str__(self):
        return self.nome
