from django.db import models

from catalog.models.base import SoftDeleteModel, TimestampedModel


class TipoLancamento(models.TextChoices):
    CUSTO = "CUSTO", "Custo"
    RECEITA = "RECEITA", "Receita"
    DESPESA = "DESPESA", "Despesa"


class StatusLancamento(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    PAGO = "PAGO", "Pago"


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
    observacoes = models.TextField(blank=True, default="", verbose_name="observações")

    class Meta:
        verbose_name = "lançamento financeiro"
        verbose_name_plural = "lançamentos financeiros"
        ordering = ["-data_lancamento", "-id"]
        indexes = [
            models.Index(fields=["tipo", "data_lancamento"]),
            models.Index(fields=["status", "data_lancamento"]),
        ]

    def __str__(self):
        return f"[{self.tipo}] {self.descricao} — R$ {self.valor}"
