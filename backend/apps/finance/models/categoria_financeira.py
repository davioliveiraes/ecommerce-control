from django.db import models

from catalog.models.base import SoftDeleteModel, TimestampedModel


class CategoriaFinanceira(TimestampedModel, SoftDeleteModel):
    nome = models.CharField(max_length=80, unique=True, verbose_name="nome")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="slug")
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

    def __str__(self):
        return self.nome
