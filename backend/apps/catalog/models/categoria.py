from django.db import models

from .base import SoftDeleteModel, TimestampedModel


class Categoria(TimestampedModel, SoftDeleteModel):
    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="categorias",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    nome = models.CharField(max_length=100, verbose_name="nome")
    slug = models.SlugField(max_length=120, verbose_name="slug")
    descricao = models.TextField(blank=True, default="", verbose_name="descrição")

    class Meta:
        verbose_name = "categoria"
        verbose_name_plural = "categorias"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"], name="unique_categoria_nome_por_empresa"
            ),
            models.UniqueConstraint(
                fields=["empresa", "slug"], name="unique_categoria_slug_por_empresa"
            ),
        ]

    def __str__(self):
        return self.nome
