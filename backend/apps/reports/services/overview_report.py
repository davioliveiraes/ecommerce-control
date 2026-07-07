"""Relatório PDF da Visão Geral (layout rico, paleta preto e branco)."""

from datetime import date
from decimal import Decimal
from typing import Optional

from django.utils import timezone
from reportlab.lib import colors

from finance.models import VisaoGeralPeriodo

from .report_design import (
    SOFT_BG,
    RichReport,
    fmt_brl,
    fmt_int,
    fmt_pct,
    ratio_pct,
)

# Paleta monocromática — segue o padrão preto/branco do painel
PRETO = colors.HexColor("#111111")
PRETO_BANNER = colors.HexColor("#0A0A0A")
CINZA_BANNER = colors.HexColor("#2E2E2E")
CINZA_ESCURO = colors.HexColor("#3F3F46")
CINZA_MEDIO = colors.HexColor("#52525B")
CINZA_CLARO = colors.HexColor("#71717A")


def _label_periodo(data_inicio: Optional[date], data_fim: Optional[date]) -> str:
    if data_inicio and data_fim:
        return f"{data_inicio.strftime('%d/%m/%Y')} – {data_fim.strftime('%d/%m/%Y')}"
    if data_inicio:
        return f"a partir de {data_inicio.strftime('%d/%m/%Y')}"
    if data_fim:
        return f"até {data_fim.strftime('%d/%m/%Y')}"
    return "Todo o período"


def gerar_relatorio_visao_geral(
    empresa,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
) -> bytes:
    qs = VisaoGeralPeriodo.objects.filter(ativo=True, empresa=empresa)
    if data_inicio is not None:
        qs = qs.filter(data_fim__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_inicio__lte=data_fim)
    periodos = list(qs.order_by("data_inicio"))

    t = {
        "visitas": 0,
        "vis_cat": 0,
        "vis_prod": 0,
        "carrinhos": 0,
        "checkout_iniciado": 0,
        "checkout_entrega": 0,
        "checkout_pagamento": 0,
        "pedidos_criados": 0,
        "pedidos_pagos": 0,
        "receita": Decimal("0"),
    }
    for p in periodos:
        t["visitas"] += p.visitas
        t["vis_cat"] += p.visualizacoes_categoria
        t["vis_prod"] += p.visualizacoes_produto
        t["carrinhos"] += p.carrinhos_criados
        t["checkout_iniciado"] += p.checkout_iniciado
        t["checkout_entrega"] += p.checkout_entrega
        t["checkout_pagamento"] += p.checkout_pagamento
        t["pedidos_criados"] += p.pedidos_criados
        t["pedidos_pagos"] += p.pedidos_pagos
        t["receita"] += p.receita

    vendas = t["pedidos_pagos"]
    receita = float(t["receita"])
    ticket = receita / vendas if vendas else 0.0
    visitas = t["visitas"] or 0

    # --- montagem ------------------------------------------------------------
    r = RichReport(accent=PRETO, banner_bg=PRETO_BANNER, banner_soft=CINZA_BANNER)
    agora = timezone.localtime()
    r.set_page_footer(f"Controle Interno · {empresa.nome}")

    r.header_band(
        wordmark=empresa.nome,
        kicker=f"{empresa.nome} Ecommerce Control · Relatório de desempenho".upper(),
        title="Visão geral",
        subtitle="Panorama do comportamento de visitantes e do funil de conversão "
        "no período selecionado.",
        badge=f"VISÃO GERAL · {agora.strftime('%d/%m/%Y')}",
        meta_lines=[
            "Módulo 02 · Visão geral",
            f"Período: <b>{_label_periodo(data_inicio, data_fim)}</b>",
            f"Gerado em: <b>{agora.strftime('%d/%m/%Y')} às {agora.strftime('%H:%M')}</b>",
        ],
    )

    r.section("Visão geral")
    r.box_text(
        f"Este relatório consolida os números da loja virtual {empresa.nome} "
        "registrados a partir do painel da NuvemShop, com leitura do funil de "
        "conversão, do comportamento dos visitantes e das taxas de conversão do período."
    )

    r.section("Filtros aplicados")
    r.filters_box(
        [
            ("Período", _label_periodo(data_inicio, data_fim)),
            ("Registros no recorte", f"{len(periodos)}"),
            ("Base", "Painel Visão geral (NuvemShop)"),
        ]
    )

    if not periodos:
        r.note(
            "Nenhum período da Visão Geral foi encontrado para o intervalo selecionado. "
            "Cadastre os números a partir dos relatórios da NuvemShop para gerar este relatório.",
            accent=PRETO,
        )
        return r.gerar()

    r.section("Indicadores do período")
    r.kpi_cards(
        [
            ("Visitas", fmt_int(visitas), PRETO),
            ("Vendas", fmt_int(vendas), PRETO),
            ("Receita", fmt_brl(receita), PRETO),
            ("Ticket médio", fmt_brl(ticket), PRETO),
        ]
    )
    r.stat_cards(
        [
            ("Vis. de categoria", fmt_int(t["vis_cat"])),
            ("Vis. de produto", fmt_int(t["vis_prod"])),
            ("Carrinhos criados", fmt_int(t["carrinhos"])),
            ("Checkouts iniciados", fmt_int(t["checkout_iniciado"])),
            ("Pedidos criados", fmt_int(t["pedidos_criados"])),
        ]
    )

    r.page_break()

    # --- página 2: funil + comportamento ---
    r.section("Funil de conversão — da visita ao pedido pago")

    def passo(label, sub, valor, base_pct, pct_sub, cor):
        return {
            "label": label,
            "sub": sub,
            "valor": fmt_int(valor),
            "frac": (valor / visitas) if visitas else 0,
            "pct": fmt_pct(ratio_pct(valor, base_pct)) if base_pct else "—",
            "pct_sub": pct_sub,
            "cor": cor,
        }

    r.funnel(
        [
            passo("Visitas", "Entrada no site", visitas, visitas, "das visitas", PRETO),
            passo("Visualização de categoria", "", t["vis_cat"], visitas, "das visitas", CINZA_ESCURO),
            passo("Visualização de produto", "", t["vis_prod"], visitas, "das visitas", CINZA_ESCURO),
            passo("Carrinhos criados", "", t["carrinhos"], t["vis_prod"], "de quem viu produto", CINZA_MEDIO),
            passo("Checkout iniciado", "", t["checkout_iniciado"], t["carrinhos"], "dos carrinhos", CINZA_CLARO),
            passo("Etapa de entrega", "", t["checkout_entrega"], t["checkout_iniciado"], "dos checkouts", CINZA_CLARO),
            passo("Etapa de pagamento", "", t["checkout_pagamento"], t["checkout_entrega"], "da etapa de entrega", CINZA_CLARO),
            passo("Pedidos pagos", "", vendas, visitas, "das visitas", PRETO),
        ]
    )

    # Maior vazamento (menor taxa de avanço entre etapas consecutivas)
    etapas = [
        ("visualização de produto", "carrinho", t["vis_prod"], t["carrinhos"]),
        ("carrinho", "checkout iniciado", t["carrinhos"], t["checkout_iniciado"]),
        ("checkout iniciado", "etapa de entrega", t["checkout_iniciado"], t["checkout_entrega"]),
        ("etapa de entrega", "etapa de pagamento", t["checkout_entrega"], t["checkout_pagamento"]),
        ("etapa de pagamento", "pedido pago", t["checkout_pagamento"], vendas),
    ]
    etapas_validas = [e for e in etapas if e[2] > 0]
    if etapas_validas:
        de, para, base, fim = min(etapas_validas, key=lambda e: e[3] / e[2])
        perdidos = base - fim
        r.callout(
            f"Maior vazamento: entre {de} ({fmt_int(base)}) e {para} ({fmt_int(fim)}), "
            f"{fmt_int(perdidos)} abandonaram — apenas {fmt_pct(ratio_pct(fim, base))} avançaram. "
            "Vale priorizar essa etapa para destravar conversão.",
            accent=PRETO,
            bg=SOFT_BG,
        )

    r.section("Comportamento detalhado")
    r.two_panels(
        "Comportamento dos visitantes",
        [
            ("Total de visitas", fmt_int(visitas)),
            ("Visualização de categoria", fmt_pct(ratio_pct(t["vis_cat"], visitas)), fmt_int(t["vis_cat"])),
            ("Visualização de produto", fmt_pct(ratio_pct(t["vis_prod"], visitas)), fmt_int(t["vis_prod"])),
            ("Carrinhos criados", fmt_pct(ratio_pct(t["carrinhos"], visitas)), fmt_int(t["carrinhos"])),
        ],
        "Comportamento no checkout",
        [
            ("Checkout iniciado", fmt_int(t["checkout_iniciado"])),
            ("Etapa de entrega", fmt_pct(ratio_pct(t["checkout_entrega"], t["checkout_iniciado"])), fmt_int(t["checkout_entrega"])),
            ("Etapa de pagamento", fmt_pct(ratio_pct(t["checkout_pagamento"], t["checkout_entrega"])), fmt_int(t["checkout_pagamento"])),
            ("Pedidos criados", fmt_int(t["pedidos_criados"])),
            ("Pedidos pagos", fmt_int(vendas)),
        ],
    )

    r.page_break()

    # --- página 3: taxas de conversão + leituras ---
    conv_visitas_vendas = ratio_pct(vendas, visitas)
    conv_visitas_carrinhos = ratio_pct(t["carrinhos"], visitas)
    conv_checkouts_vendas = ratio_pct(vendas, t["checkout_iniciado"])

    r.section("Taxas de conversão (painel NuvemShop)")
    r.conversion_cards(
        [
            (fmt_pct(conv_visitas_vendas), "Visitas a vendas", "Conversão geral do site"),
            (fmt_pct(conv_visitas_carrinhos), "Visitas a carrinhos", "Intenção de compra gerada"),
            (fmt_pct(conv_checkouts_vendas), "Checkouts a vendas", "Eficiência do checkout"),
        ],
        accent=PRETO,
    )
    r.note(
        "As taxas acima são consolidadas a partir dos relatórios da NuvemShop e podem usar "
        "bases (sessões únicas) distintas das contagens absolutas do funil — por isso pode "
        "haver pequena divergência em relação aos percentuais calculados sobre as visitas.",
        accent=PRETO,
    )

    r.section("Principais leituras")
    r.numbered_list(
        [
            (
                "Topo de funil.",
                f"{fmt_pct(ratio_pct(t['vis_cat'], visitas))} das visitas chegaram a uma categoria e "
                f"{fmt_pct(ratio_pct(t['vis_prod'], visitas))} a uma página de produto — sinal de interesse no catálogo.",
            ),
            (
                "Produto para carrinho.",
                f"Dos {fmt_int(t['vis_prod'])} que viram produto, {fmt_int(t['carrinhos'])} criaram carrinho "
                f"({fmt_pct(ratio_pct(t['carrinhos'], t['vis_prod']))}). Revisar preço visível, frete estimado e CTA na página de produto.",
            ),
            (
                "Conversão do checkout.",
                f"{fmt_pct(conv_checkouts_vendas)} dos checkouts iniciados viraram venda "
                f"({fmt_int(vendas)} de {fmt_int(t['checkout_iniciado'])}).",
            ),
            (
                "Volume e ticket.",
                f"{fmt_int(vendas)} vendas, {fmt_brl(receita)} de receita e ticket médio de {fmt_brl(ticket)} no período.",
            ),
        ],
        accent=PRETO,
    )

    r.page_break()

    # --- página 4: recomendações + detalhamento dos períodos ---
    r.section("Recomendações")
    r.numbered_list(
        [
            (
                "Atacar o maior vazamento do funil.",
                "Priorize a etapa com menor taxa de avanço identificada acima antes de investir em mais tráfego.",
            ),
            (
                "Reduzir atrito produto → carrinho.",
                "Reforce preço, frete estimado e prova social na página de produto, onde costuma ocorrer a primeira grande queda.",
            ),
            (
                "Acionar recuperação de checkout abandonado.",
                "Use os templates transacionais para resgatar carrinhos e checkouts não concluídos.",
            ),
        ],
        accent=PRETO,
    )

    r.section("Detalhamento dos períodos")
    # Resumo antes da tabela: se ela quebrar de página, os totais não ficam
    # órfãos em uma página quase vazia.
    r.filters_box(
        [
            ("Períodos no recorte", f"{len(periodos)}"),
            ("Receita total", fmt_brl(receita)),
        ]
    )
    linhas = [
        [
            f"{p.data_inicio.strftime('%d/%m/%Y')} – {p.data_fim.strftime('%d/%m/%Y')}",
            fmt_int(p.visitas),
            fmt_int(p.carrinhos_criados),
            fmt_int(p.checkout_iniciado),
            fmt_int(p.pedidos_pagos),
            fmt_brl(p.receita),
            fmt_brl(p.ticket_medio),
        ]
        for p in reversed(periodos)
    ]
    r.data_table(
        ["Período", "Visitas", "Carrinhos", "Checkouts", "Pedidos pagos", "Receita", "Ticket médio"],
        linhas,
        fracs=[2.2, 1.0, 1.0, 1.0, 1.2, 1.3, 1.2],
        aligns=["L", "R", "R", "R", "R", "R", "R"],
    )

    return r.gerar()
