from decimal import Decimal
from typing import List, Optional, Union

from ninja import Router, Schema

from finance.services import analytics_service

router = Router(tags=["finance:analytics"])


class KpiSerie(Schema):
    valor: Union[int, Decimal]
    formato: str  # "inteiro" | "moeda"
    serie: List[Union[int, Decimal]]
    labels: List[str]


class KpiOverviewSet(Schema):
    visitas: KpiSerie
    vendas: KpiSerie
    receita: KpiSerie
    ticket_medio: KpiSerie


class BehaviorItem(Schema):
    label: str
    valor: int


class ConversionItem(Schema):
    label: str
    valor_percentual: float
    detalhe: Optional[str] = None


class AnalyticsOverviewResponse(Schema):
    ultima_atualizacao: str
    kpis: KpiOverviewSet
    comportamento_visitantes: List[BehaviorItem]
    comportamento_checkout: List[BehaviorItem]
    conversoes: List[ConversionItem]


class ProdutoRanking(Schema):
    sku: str
    nome: str
    marca: str
    valor_principal: str
    valor_secundario: Optional[str] = None


class AnalyticsProdutosResponse(Schema):
    mais_vendidos: List[ProdutoRanking]
    mais_visualizados: List[ProdutoRanking]
    estoque_critico: List[ProdutoRanking]
    margem_ranking: List[ProdutoRanking]


@router.get("/overview", response=AnalyticsOverviewResponse)
def overview(request):
    """Estatísticas estilo Nuvemshop — visitas, comportamento, checkout e conversões."""
    return analytics_service.build_overview()


@router.get("/products", response=AnalyticsProdutosResponse)
def products(request):
    """Rankings de produtos: mais vendidos, mais visualizados, estoque crítico e margem."""
    return analytics_service.build_products()
