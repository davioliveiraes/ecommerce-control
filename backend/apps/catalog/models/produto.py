from django.db import models

from .base import SoftDeleteModel, TimestampedModel


class Produto(TimestampedModel, SoftDeleteModel):
    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="produtos",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    nome_gestaoclick = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="nome curto (GestãoClick)",
        help_text="Rótulo curto opcional para o produto no GestãoClick.",
    )
    nome_site = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="nome curto (site)",
        help_text="Rótulo curto opcional para o produto no Nuvemshop.",
    )
    descricao_produto_gestaoclick = models.TextField(
        blank=True,
        default="",
        verbose_name="descrição do produto (GestãoClick)",
        help_text="Descrição longa do produto no GestãoClick.",
    )
    descricao_produto_site = models.TextField(
        blank=True,
        default="",
        verbose_name="descrição do produto (site)",
        help_text="Descrição longa do produto no Nuvemshop.",
    )
    marca = models.ForeignKey(
        "catalog.Marca",
        on_delete=models.PROTECT,
        related_name="produtos",
        null=True,
        blank=True,
        verbose_name="marca",
    )
    subcategoria = models.ForeignKey(
        "catalog.Subcategoria",
        on_delete=models.PROTECT,
        related_name="produtos",
        null=True,
        blank=True,
        verbose_name="subcategoria",
    )

    class Meta:
        verbose_name = "produto"
        verbose_name_plural = "produtos"
        ordering = ["descricao_produto_site"]

    def __str__(self):
        return self.nome_site or self.descricao_produto_site or f"produto #{self.pk}"
