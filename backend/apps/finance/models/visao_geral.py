from decimal import Decimal

from django.db import models

from catalog.models.base import SoftDeleteModel, TimestampedModel


class VisaoGeralPeriodo(TimestampedModel, SoftDeleteModel):
    """
    Snapshot de métricas da loja para um período definido pelo analista.

    Controle interno: os números são preenchidos manualmente a partir dos
    relatórios emitidos na NuvemShop. Não há integração com a API — cada
    período é um registro digitado pelo analista de ecommerce.
    """

    empresa = models.ForeignKey(
        "accounts.Empresa",
        on_delete=models.CASCADE,
        related_name="periodos_visao_geral",
        null=True,
        blank=True,
        verbose_name="empresa",
    )
    data_inicio = models.DateField(verbose_name="início do período")
    data_fim = models.DateField(verbose_name="fim do período")

    visitas = models.PositiveIntegerField(default=0, verbose_name="visitas")
    visualizacoes_categoria = models.PositiveIntegerField(
        default=0, verbose_name="visualizações de categoria"
    )
    visualizacoes_produto = models.PositiveIntegerField(
        default=0, verbose_name="visualizações de produto"
    )
    carrinhos_criados = models.PositiveIntegerField(
        default=0, verbose_name="carrinhos criados"
    )

    checkout_iniciado = models.PositiveIntegerField(
        default=0, verbose_name="checkout iniciado"
    )
    checkout_entrega = models.PositiveIntegerField(
        default=0, verbose_name="etapa de entrega"
    )
    checkout_pagamento = models.PositiveIntegerField(
        default=0, verbose_name="etapa de pagamento"
    )
    pedidos_criados = models.PositiveIntegerField(
        default=0, verbose_name="pedidos criados"
    )
    pedidos_pagos = models.PositiveIntegerField(
        default=0,
        verbose_name="pedidos pagos",
        help_text="Pedidos pagos no período. Equivale ao total de vendas.",
    )

    receita = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        verbose_name="receita",
    )

    observacao = models.TextField(blank=True, default="", verbose_name="observação")

    class Meta:
        verbose_name = "período da visão geral"
        verbose_name_plural = "períodos da visão geral"
        ordering = ["-data_inicio", "-id"]
        indexes = [
            models.Index(fields=["data_inicio", "data_fim"]),
        ]

    def __str__(self):
        return f"Visão geral {self.data_inicio} → {self.data_fim}"

    @property
    def vendas(self) -> int:
        return self.pedidos_pagos

    @property
    def ticket_medio(self) -> Decimal:
        if not self.pedidos_pagos:
            return Decimal("0")
        return (self.receita / self.pedidos_pagos).quantize(Decimal("0.01"))

    @property
    def conversao_visitas_vendas(self) -> Decimal:
        if not self.visitas:
            return Decimal("0")
        return (Decimal(self.pedidos_pagos) / self.visitas * 100).quantize(
            Decimal("0.01")
        )

    @property
    def conversao_visitas_carrinhos(self) -> Decimal:
        if not self.visitas:
            return Decimal("0")
        return (Decimal(self.carrinhos_criados) / self.visitas * 100).quantize(
            Decimal("0.01")
        )

    @property
    def conversao_checkouts_vendas(self) -> Decimal:
        if not self.checkout_iniciado:
            return Decimal("0")
        return (Decimal(self.pedidos_pagos) / self.checkout_iniciado * 100).quantize(
            Decimal("0.01")
        )
