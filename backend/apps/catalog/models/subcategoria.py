from django.db import models

from .base import SoftDeleteModel, TimestampedModel


class Subcategoria(TimestampedModel, SoftDeleteModel):
    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="subcategorias",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    nome = models.CharField(max_length=100, verbose_name="nome")
    slug = models.SlugField(max_length=120, verbose_name="slug")
    categoria = models.ForeignKey(
        "catalog.Categoria",
        on_delete=models.PROTECT,
        related_name="subcategorias",
        verbose_name="categoria",
    )

    class Meta:
        verbose_name = "subcategoria"
        verbose_name_plural = "subcategorias"
        ordering = ["categoria__nome", "nome"]
        constraints = [
            models.UniqueConstraint(
                fields=["categoria", "nome"],
                name="unique_subcategoria_nome_por_categoria",
            ),
            models.UniqueConstraint(
                fields=["categoria", "slug"],
                name="unique_subcategoria_slug_por_categoria",
            ),
        ]

    def __str__(self):
        return f"{self.categoria.nome} > {self.nome}"
