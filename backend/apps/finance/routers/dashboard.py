from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import List, Optional

from django.db.models import Max, Min, Sum
from ninja import Router, Schema

from accounts.tenancy import empresa_do_usuario
from finance.models import LancamentoFinanceiro

router = Router(tags=["finance:dashboard"])


class KpiCard(Schema):
    custo_total: Decimal
    receita_total: Decimal
    despesa_total: Decimal
    lucro: Decimal  # receita - (custo + despesa)


class PontoMensal(Schema):
    mes: str  # formato "2026-05"
    custo: Decimal
    receita: Decimal
    despesa: Decimal


class FatiaCategoria(Schema):
    categoria_id: Optional[int]
    categoria_nome: str
    categoria_cor_hex: str
    valor: Decimal


class PeriodoCategoria(Schema):
    categoria_id: Optional[int]
    data_inicio: date
    data_fim: date


class PeriodoGeral(Schema):
    data_inicio: date
    data_fim: date


class MetricaReceitaVendas(Schema):
    chave: str
    nome: str
    receita: Decimal
    vendas: int


class DashboardResponse(Schema):
    kpis: KpiCard
    serie_mensal: List[PontoMensal]
    receitas_por_categoria: List[FatiaCategoria]
    despesas_por_categoria: List[FatiaCategoria]
    custos_por_categoria: List[FatiaCategoria]
    periodo_geral: Optional[PeriodoGeral]
    periodos_por_categoria: List[PeriodoCategoria]
    receita_vendas_por_forma_pagamento: List[MetricaReceitaVendas]
    receita_vendas_por_meio_pagamento: List[MetricaReceitaVendas]
    receita_vendas_por_parcelas: List[MetricaReceitaVendas]


FORMA_PAGAMENTO_LABELS = {
    "PIX": "Pix",
    "CARTAO_CREDITO": "Cartão de crédito",
    "BOLETO": "Boleto",
    "NUVEMPAGO": "NuvemPago",
    "OUTRO": "Outro",
}

MEIO_PAGAMENTO_LABELS = {
    "NUVEMPAGO": "NuvemPago",
    "MERCADO_PAGO": "Mercado Pago",
    "PAGSEGURO": "PagSeguro",
    "MANUAL": "Manual",
    "OUTRO": "Outro",
}


@router.get("/", response=DashboardResponse)
def dashboard(
    request,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    categoria_id: Optional[int] = None,
    tipo: Optional[str] = None,
    incluir_pendentes: bool = False,
):
    """
    Retorna agregados para o dashboard financeiro.

    - Por padrão, considera só PAGOS (cash real).
    - `?incluir_pendentes=true` soma PENDENTES também (visão accrual).
    - Filtros opcionais de data: ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD.
    """
    base_qs = LancamentoFinanceiro.objects.filter(
        ativo=True, empresa=empresa_do_usuario(request)
    ).select_related("categoria")
    periodo_geral_agregado = base_qs.aggregate(
        data_inicio=Min("data_lancamento"),
        data_fim=Max("data_lancamento"),
    )
    periodo_geral = None
    if periodo_geral_agregado["data_inicio"] and periodo_geral_agregado["data_fim"]:
        periodo_geral = PeriodoGeral(
            data_inicio=periodo_geral_agregado["data_inicio"],
            data_fim=periodo_geral_agregado["data_fim"],
        )

    qs = base_qs
    if not incluir_pendentes:
        qs = qs.filter(status="PAGO")

    periodo_qs = qs

    if data_inicio is not None:
        qs = qs.filter(data_lancamento__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_lancamento__lte=data_fim)
    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)
    if tipo:
        qs = qs.filter(tipo=tipo)

    totais_por_tipo = qs.values("tipo").annotate(total=Sum("valor"))
    mapa_totais = {
        item["tipo"]: item["total"] or Decimal("0") for item in totais_por_tipo
    }
    custo_total = mapa_totais.get("CUSTO", Decimal("0"))
    receita_total = mapa_totais.get("RECEITA", Decimal("0"))
    despesa_total = mapa_totais.get("DESPESA", Decimal("0"))
    lucro = receita_total - (custo_total + despesa_total)

    serie_dict: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {
            "custo": Decimal("0"),
            "receita": Decimal("0"),
            "despesa": Decimal("0"),
        }
    )
    for lancamento in qs:
        chave = lancamento.data_lancamento.strftime("%Y-%m")
        if lancamento.tipo == "CUSTO":
            serie_dict[chave]["custo"] += lancamento.valor
        elif lancamento.tipo == "RECEITA":
            serie_dict[chave]["receita"] += lancamento.valor
        elif lancamento.tipo == "DESPESA":
            serie_dict[chave]["despesa"] += lancamento.valor
    serie_mensal = [
        PontoMensal(mes=mes, **valores)
        for mes, valores in sorted(serie_dict.items())
    ]

    def agregar_por_categoria(tipo: str) -> List[FatiaCategoria]:
        agregados = (
            qs.filter(tipo=tipo)
            .values("categoria_id", "categoria__nome", "categoria__cor_hex")
            .annotate(total=Sum("valor"))
            .order_by("-total")
        )
        resultado = []
        for item in agregados:
            resultado.append(
                FatiaCategoria(
                    categoria_id=item["categoria_id"],
                    categoria_nome=item["categoria__nome"] or "Sem categoria",
                    categoria_cor_hex=item["categoria__cor_hex"] or "",
                    valor=item["total"] or Decimal("0"),
                )
            )
        return resultado

    receitas = qs.filter(tipo="RECEITA")

    periodos_por_categoria = []
    for item in (
        periodo_qs.values("categoria_id")
        .annotate(data_inicio=Min("data_lancamento"), data_fim=Max("data_lancamento"))
        .order_by("categoria_id")
    ):
        if item["data_inicio"] and item["data_fim"]:
            periodos_por_categoria.append(
                PeriodoCategoria(
                    categoria_id=item["categoria_id"],
                    data_inicio=item["data_inicio"],
                    data_fim=item["data_fim"],
                )
            )

    def agregar_receita_vendas(
        campo: str,
        labels: Optional[dict[str, str]] = None,
    ) -> List[MetricaReceitaVendas]:
        agregados = (
            receitas.values(campo)
            .annotate(receita=Sum("valor"), vendas=Sum("quantidade_vendas"))
            .order_by("-receita")
        )
        resultado = []
        for item in agregados:
            chave = item[campo]
            if chave in (None, ""):
                chave = "NAO_INFORMADO"
            nome = labels.get(chave, chave) if labels else str(chave)
            if campo == "quantidade_parcelas":
                nome = "Não informado" if chave == "NAO_INFORMADO" else f"{chave}x"
            elif chave == "NAO_INFORMADO":
                nome = "Não informado"
            resultado.append(
                MetricaReceitaVendas(
                    chave=str(chave),
                    nome=nome,
                    receita=item["receita"] or Decimal("0"),
                    vendas=item["vendas"] or 0,
                )
            )
        return resultado

    return DashboardResponse(
        kpis=KpiCard(
            custo_total=custo_total,
            receita_total=receita_total,
            despesa_total=despesa_total,
            lucro=lucro,
        ),
        serie_mensal=serie_mensal,
        receitas_por_categoria=agregar_por_categoria("RECEITA"),
        despesas_por_categoria=agregar_por_categoria("DESPESA"),
        custos_por_categoria=agregar_por_categoria("CUSTO"),
        periodo_geral=periodo_geral,
        periodos_por_categoria=periodos_por_categoria,
        receita_vendas_por_forma_pagamento=agregar_receita_vendas(
            "forma_pagamento",
            FORMA_PAGAMENTO_LABELS,
        ),
        receita_vendas_por_meio_pagamento=agregar_receita_vendas(
            "meio_pagamento",
            MEIO_PAGAMENTO_LABELS,
        ),
        receita_vendas_por_parcelas=agregar_receita_vendas("quantidade_parcelas"),
    )
