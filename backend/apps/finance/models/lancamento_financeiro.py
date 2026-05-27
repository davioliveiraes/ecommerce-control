from django.db import models

from catalog.models.base import SoftDeleteModel, TimestampedModel


class TipoLancamento(models.TextChoices):
    CUSTO = "CUSTO", "Custo"
    RECEITA = "RECEITA", "Receita"
    DESPESA = "DESPESA", "Despesa"


class StatusLancamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PAGO = "PAGO", "Pago"


class FormaPagamento(models.TextChoices):
    PIX = "PIX", "Pix"
    CARTAO_CREDITO = "CARTAO_CREDITO", "Cartão de crédito"
    BOLETO = "BOLETO", "Boleto"
    NUVEMPAGO = "NUVEMPAGO", "NuvemPago"
    OUTRO = "OUTRO", "Outro"


class MeioPagamento(models.TextChoices):
    NUVEMPAGO = "NUVEMPAGO", "NuvemPago"
    MERCADO_PAGO = "MERCADO_PAGO", "Mercado Pago"
    PAGSEGURO = "PAGSEGURO", "PagSeguro"
    MANUAL = "MANUAL", "Manual"
    OUTRO = "OUTRO", "Outro"


class LancamentoFinanceiro(TimestampedModel, SoftDeleteModel):
    descricao = models.CharField(max_length=255, verbose_name="descrição")
    tipo = models.CharField(
        max_length=10,
        choices=TipoLancamento.choices,
        verbose_name="tipo",
    )
    categoria = models.ForeignKey(
        "finance.CategoriaFinanceira",
        on_delete=models.PROTECT,
        related_name="lancamentos",
        null=True,
        blank=True,
        verbose_name="categoria",
    )
    valor = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="valor",
        help_text="Sempre positivo; o sinal vem do tipo (CUSTO/DESPESA saem, RECEITA entra).",
    )
    data_lancamento = models.DateField(verbose_name="data do lançamento")
    status = models.CharField(
        max_length=10,
        choices=StatusLancamento.choices,
        default=StatusLancamento.PENDENTE,
        verbose_name="status",
    )
    forma_pagamento = models.CharField(
        max_length=20,
        choices=FormaPagamento.choices,
        blank=True,
        default="",
        verbose_name="forma de pagamento",
    )
    meio_pagamento = models.CharField(
        max_length=20,
        choices=MeioPagamento.choices,
        blank=True,
        default="",
        verbose_name="meio/provedor de pagamento",
    )
    quantidade_parcelas = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name="quantidade de parcelas",
    )
    quantidade_vendas = models.PositiveIntegerField(
        default=1,
        verbose_name="quantidade de vendas",
        help_text="Quantidade de vendas agregadas neste lançamento. Use 1 para lançamento individual.",
    )
    fonte_trafego = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="fonte de tráfego",
    )
    observacoes = models.TextField(blank=True, default="", verbose_name="observações")

    class Meta:
        verbose_name = "lançamento financeiro"
        verbose_name_plural = "lançamentos financeiros"
        ordering = ["-data_lancamento", "-id"]
        indexes = [
            models.Index(fields=["tipo", "data_lancamento"]),
            models.Index(fields=["status", "data_lancamento"]),
            models.Index(fields=["forma_pagamento", "data_lancamento"]),
            models.Index(fields=["meio_pagamento", "data_lancamento"]),
            models.Index(fields=["fonte_trafego", "data_lancamento"]),
        ]

    def __str__(self):
        return f"[{self.tipo}] {self.descricao} — R$ {self.valor}"
