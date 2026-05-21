from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import List, Optional

from django.db.models import Sum
from ninja import Router, Schema

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


class DashboardResponse(Schema):
    kpis: KpiCard
    serie_mensal: List[PontoMensal]
    despesas_por_categoria: List[FatiaCategoria]
    custos_por_categoria: List[FatiaCategoria]


@router.get("/", response=DashboardResponse)
def dashboard(
    request,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    incluir_pendentes: bool = False,
):
    """
    Retorna agregados para o dashboard financeiro.

    - Por padrão, considera só PAGOS (cash real).
    - `?incluir_pendentes=true` soma PENDENTES também (visão accrual).
    - Filtros opcionais de data: ?data_inicio=YYYY-MM-DD&data_fim=YYYY-MM-DD.
    """
    qs = LancamentoFinanceiro.objects.filter(ativo=True).select_related("categoria")
    if not incluir_pendentes:
        qs = qs.filter(status="PAGO")
    if data_inicio is not None:
        qs = qs.filter(data_lancamento__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_lancamento__lte=data_fim)

    # 1. KPIs
    totais_por_tipo = qs.values("tipo").annotate(total=Sum("valor"))
    mapa_totais = {
        item["tipo"]: item["total"] or Decimal("0") for item in totais_por_tipo
    }
    custo_total = mapa_totais.get("CUSTO", Decimal("0"))
    receita_total = mapa_totais.get("RECEITA", Decimal("0"))
    despesa_total = mapa_totais.get("DESPESA", Decimal("0"))
    lucro = receita_total - (custo_total + despesa_total)

    # 2. Série mensal
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

    # 3. Pizza por categoria
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

    return DashboardResponse(
        kpis=KpiCard(
            custo_total=custo_total,
            receita_total=receita_total,
            despesa_total=despesa_total,
            lucro=lucro,
        ),
        serie_mensal=serie_mensal,
        despesas_por_categoria=agregar_por_categoria("DESPESA"),
        custos_por_categoria=agregar_por_categoria("CUSTO"),
    )
