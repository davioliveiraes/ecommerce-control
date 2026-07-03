from django.db import models

from .base import SoftDeleteModel, TimestampedModel


class Marca(TimestampedModel, SoftDeleteModel):
    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="marcas",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    nome = models.CharField(max_length=100, verbose_name="nome")
    slug = models.SlugField(max_length=120, verbose_name="slug")

    class Meta:
        verbose_name = "marca"
        verbose_name_plural = "marcas"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"], name="unique_marca_nome_por_empresa"
            ),
            models.UniqueConstraint(
                fields=["empresa", "slug"], name="unique_marca_slug_por_empresa"
            ),
        ]

    def __str__(self):
        return self.nome
