"""
Deterministic analytics mock service.

Simula estatísticas estilo Nuvemshop (visitas, comportamento, checkout, rankings de produtos).
Os números são gerados com semente fixa a partir de dados reais do catálogo, de forma que
o resultado seja reproducível em qualquer ambiente e coerente com o catálogo seedado.
"""
from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

from catalog.models import Variacao


SEED = 42
SPARKLINE_POINTS = 7


def _rng(salt: str) -> random.Random:
    return random.Random(f"{SEED}-{salt}")


def _sparkline(rng: random.Random, base: int, variance: float = 0.4) -> List[int]:
    points: List[int] = []
    current = float(base)
    for _ in range(SPARKLINE_POINTS):
        delta = rng.uniform(-variance, variance) * base
        current = max(0.0, current + delta)
        points.append(int(round(current)))
    return points


def build_overview() -> dict:
    rng = _rng("overview")

    visitas_total = rng.randint(2800, 5200)
    visitas_serie = _sparkline(rng, visitas_total // SPARKLINE_POINTS, variance=0.35)
    visitas_total = sum(visitas_serie)

    taxa_conversao = rng.uniform(0.018, 0.035)
    vendas_total = max(1, int(round(visitas_total * taxa_conversao)))
    vendas_serie = [
        max(0, int(round(v * taxa_conversao * rng.uniform(0.7, 1.3))))
        for v in visitas_serie
    ]

    ticket_base = rng.uniform(180.0, 320.0)
    receita_serie = [
        round(v * ticket_base * rng.uniform(0.9, 1.1), 2) for v in vendas_serie
    ]
    receita_total = round(sum(receita_serie), 2)

    ticket_medio = round(receita_total / vendas_total, 2) if vendas_total else 0.0
    ticket_serie = [
        round(r / v, 2) if v else 0.0 for r, v in zip(receita_serie, vendas_serie)
    ]

    visualizacao_categoria = int(round(visitas_total * rng.uniform(0.38, 0.52)))
    visualizacao_produto = int(round(visitas_total * rng.uniform(0.55, 0.72)))
    carrinhos_criados = int(round(visitas_total * rng.uniform(0.06, 0.11)))

    checkout_iniciado = int(round(carrinhos_criados * rng.uniform(0.55, 0.75)))
    etapa_entrega = int(round(checkout_iniciado * rng.uniform(0.78, 0.92)))
    etapa_pagamento = int(round(etapa_entrega * rng.uniform(0.80, 0.93)))
    pedidos_criados = int(round(etapa_pagamento * rng.uniform(0.82, 0.95)))
    pedidos_pagos = max(vendas_total, int(round(pedidos_criados * rng.uniform(0.88, 0.97))))

    visitas_a_vendas = (vendas_total / visitas_total * 100) if visitas_total else 0.0
    visitas_carrinhos = (carrinhos_criados / visitas_total * 100) if visitas_total else 0.0
    checkouts_vendas = (vendas_total / checkout_iniciado * 100) if checkout_iniciado else 0.0

    agora = datetime.now(timezone.utc).astimezone()

    return {
        "ultima_atualizacao": agora.isoformat(timespec="minutes"),
        "kpis": {
            "visitas": {
                "valor": visitas_total,
                "formato": "inteiro",
                "serie": visitas_serie,
                "labels": _serie_labels(),
            },
            "vendas": {
                "valor": vendas_total,
                "formato": "inteiro",
                "serie": vendas_serie,
                "labels": _serie_labels(),
            },
            "receita": {
                "valor": Decimal(str(receita_total)),
                "formato": "moeda",
                "serie": [Decimal(str(v)) for v in receita_serie],
                "labels": _serie_labels(),
            },
            "ticket_medio": {
                "valor": Decimal(str(ticket_medio)),
                "formato": "moeda",
                "serie": [Decimal(str(v)) for v in ticket_serie],
                "labels": _serie_labels(),
            },
        },
        "comportamento_visitantes": [
            {"label": "Total de visitas", "valor": visitas_total},
            {"label": "Visualização de categoria", "valor": visualizacao_categoria},
            {"label": "Visualização de produto", "valor": visualizacao_produto},
            {"label": "Carrinhos criados", "valor": carrinhos_criados},
        ],
        "comportamento_checkout": [
            {"label": "Checkout iniciado", "valor": checkout_iniciado},
            {"label": "Etapa de entrega", "valor": etapa_entrega},
            {"label": "Etapa de pagamento", "valor": etapa_pagamento},
            {"label": "Pedidos criados", "valor": pedidos_criados},
            {"label": "Pedidos pagos", "valor": pedidos_pagos},
        ],
        "conversoes": [
            {
                "label": "Visitas para vendas",
                "valor_percentual": round(visitas_a_vendas, 2),
                "detalhe": f"{vendas_total} pedidos em {visitas_total} visitas",
            },
            {
                "label": "Visitas para carrinhos",
                "valor_percentual": round(visitas_carrinhos, 2),
                "detalhe": f"{carrinhos_criados} carrinhos criados",
            },
            {
                "label": "Checkouts para vendas",
                "valor_percentual": round(checkouts_vendas, 2),
                "detalhe": f"{vendas_total} pedidos em {checkout_iniciado} checkouts",
            },
        ],
    }


def _serie_labels() -> List[str]:
    """Datas dos últimos N dias (incluindo hoje), no formato dd/mm."""
    hoje = datetime.now()
    return [
        (hoje - timedelta(days=SPARKLINE_POINTS - 1 - i)).strftime("%d/%m")
        for i in range(SPARKLINE_POINTS)
    ]


def build_products() -> dict:
    """Rankings de produtos baseados no catálogo real, com métricas mockadas determinísticas."""
    variacoes = list(
        Variacao.objects.filter(ativo=True)
        .select_related("produto", "produto__marca")
        .order_by("id")[:120]
    )

    if not variacoes:
        return {
            "mais_vendidos": [],
            "mais_visualizados": [],
            "estoque_critico": [],
            "margem_ranking": [],
        }

    rng_vendas = _rng("vendas")
    rng_views = _rng("views")
    rng_estoque = _rng("estoque")

    enriched = []
    for variacao in variacoes:
        nome = _nome_variacao(variacao)
        marca = variacao.produto.marca.nome if variacao.produto.marca_id else "Sem marca"
        vendas = rng_vendas.randint(0, 95)
        receita = (variacao.preco_site or variacao.preco_loja or Decimal("0")) * vendas
        views = rng_views.randint(20, 800)
        estoque = rng_estoque.choices(
            [0, 1, 2, 3, 5, 8, 14, 25, 60, 120],
            weights=[3, 4, 5, 6, 7, 9, 12, 15, 22, 17],
            k=1,
        )[0]
        margem = variacao.margem_percentual or Decimal("0")
        enriched.append(
            {
                "variacao": variacao,
                "nome": nome,
                "marca": marca,
                "vendas": vendas,
                "receita": receita,
                "views": views,
                "estoque": estoque,
                "margem": margem,
            }
        )

    mais_vendidos = sorted(enriched, key=lambda x: x["vendas"], reverse=True)[:8]
    mais_visualizados = sorted(enriched, key=lambda x: x["views"], reverse=True)[:8]
    estoque_critico = [x for x in enriched if x["estoque"] <= 3]
    estoque_critico = sorted(estoque_critico, key=lambda x: (x["estoque"], -x["views"]))[:8]
    margem_ranking = sorted(enriched, key=lambda x: x["margem"], reverse=True)[:8]

    return {
        "mais_vendidos": [
            {
                "sku": x["variacao"].sku_nuvemshop or f"#{x['variacao'].id}",
                "nome": x["nome"],
                "marca": x["marca"],
                "valor_principal": str(x["vendas"]),
                "valor_secundario": _moeda(x["receita"]),
            }
            for x in mais_vendidos
        ],
        "mais_visualizados": [
            {
                "sku": x["variacao"].sku_nuvemshop or f"#{x['variacao'].id}",
                "nome": x["nome"],
                "marca": x["marca"],
                "valor_principal": str(x["views"]),
                "valor_secundario": f"{x['vendas']} vendas",
            }
            for x in mais_visualizados
        ],
        "estoque_critico": [
            {
                "sku": x["variacao"].sku_nuvemshop or f"#{x['variacao'].id}",
                "nome": x["nome"],
                "marca": x["marca"],
                "valor_principal": _estoque_label(x["estoque"]),
                "valor_secundario": f"{x['vendas']} vendas no período",
            }
            for x in estoque_critico
        ],
        "margem_ranking": [
            {
                "sku": x["variacao"].sku_nuvemshop or f"#{x['variacao'].id}",
                "nome": x["nome"],
                "marca": x["marca"],
                "valor_principal": f"{float(x['margem']):.1f}%",
                "valor_secundario": _moeda(x["receita"]),
            }
            for x in margem_ranking
        ],
    }


def _nome_variacao(variacao: Variacao) -> str:
    produto_nome = variacao.produto.nome_site or variacao.produto.descricao_produto_site or f"Produto #{variacao.produto_id}"
    descricao = (variacao.descricao or "").strip()
    if descricao:
        return f"{produto_nome} — {descricao}"
    return produto_nome


def _moeda(valor: Decimal) -> str:
    quantizado = Decimal(valor).quantize(Decimal("0.01"))
    return f"R$ {quantizado:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _estoque_label(qtd: int) -> str:
    if qtd == 0:
        return "Sem estoque"
    if qtd == 1:
        return "1 unidade"
    return f"{qtd} unidades"
