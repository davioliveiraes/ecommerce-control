from django.db import models

from catalog.models.base import SoftDeleteModel, TimestampedModel


class CategoriaFinanceira(TimestampedModel, SoftDeleteModel):
    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="categorias_financeiras",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    nome = models.CharField(max_length=80, verbose_name="nome")
    slug = models.SlugField(max_length=100, verbose_name="slug")
    cor_hex = models.CharField(
        max_length=7,
        blank=True,
        default="",
        verbose_name="cor (hex)",
        help_text="Cor opcional para gráfico de pizza, ex: #f97316",
    )

    class Meta:
        verbose_name = "categoria financeira"
        verbose_name_plural = "categorias financeiras"
        ordering = ["nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "nome"],
                name="unique_categoria_financeira_nome_por_empresa",
            ),
            models.UniqueConstraint(
                fields=["empresa", "slug"],
                name="unique_categoria_financeira_slug_por_empresa",
            ),
        ]

    def __str__(self):
        return self.nome
