"""Relatório PDF da Visão Geral (desempenho da loja) no layout rico."""

from datetime import date
from decimal import Decimal
from typing import Optional

from django.utils import timezone

from finance.models import VisaoGeralPeriodo

from .report_design import (
    GREEN,
    NAVY,
    NAVY_SOFT,
    ORANGE,
    PURPLE,
    PURPLE_SOFT,
    RichReport,
    fmt_brl,
    fmt_int,
    fmt_pct,
    ratio_pct,
)


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

    r = RichReport()
    agora = timezone.localtime()

    # --- Página 1: cabeçalho + KPIs ---
    r.header_band(
        wordmark=empresa.nome,
        kicker="RELATÓRIO DE DESEMPENHO — LOJA VIRTUAL",
        title="Visão geral da loja",
        subtitle="Panorama do comportamento de visitantes e do funil de conversão "
        "no período selecionado.",
        badge=f"PERÍODO · {len(periodos)} REGISTRO(S)",
        meta_lines=[
            f"Período: <b>{_label_periodo(data_inicio, data_fim)}</b>",
            f"Gerado em: <b>{agora.strftime('%d/%m/%Y %H:%M')}</b>",
            "Base: data de criação do pedido",
        ],
    )

    if not periodos:
        r.section("Sem dados no período")
        r.note(
            "Nenhum período da Visão Geral foi encontrado para o intervalo selecionado. "
            "Cadastre os números a partir dos relatórios da NuvemShop para gerar este relatório."
        )
        return r.gerar()

    r.section("Indicadores do período")
    r.kpi_cards(
        [
            ("Visitas", fmt_int(visitas), NAVY),
            ("Vendas", fmt_int(vendas), ORANGE),
            ("Receita", fmt_brl(receita), ORANGE),
            ("Ticket médio", fmt_brl(ticket), PURPLE),
        ]
    )

    r.page_break()

    # --- Página 2: funil + comportamento ---
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
            passo("Visitas", "Entrada no site", visitas, visitas, "das visitas", NAVY),
            passo("Visualização de categoria", "", t["vis_cat"], visitas, "das visitas", NAVY_SOFT),
            passo("Visualização de produto", "", t["vis_prod"], visitas, "das visitas", PURPLE_SOFT),
            passo("Carrinhos criados", "", t["carrinhos"], t["vis_prod"], "de quem viu produto", PURPLE),
            passo("Checkout iniciado", "", t["checkout_iniciado"], t["carrinhos"], "dos carrinhos", ORANGE),
            passo("Etapa de entrega", "", t["checkout_entrega"], t["checkout_iniciado"], "dos checkouts", ORANGE),
            passo("Etapa de pagamento", "", t["checkout_pagamento"], t["checkout_entrega"], "da etapa de entrega", ORANGE),
            passo("Pedidos pagos", "", vendas, visitas, "das visitas", GREEN),
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
            f"Maior vazamento: entre <b>{de} ({fmt_int(base)})</b> e <b>{para} ({fmt_int(fim)})</b>, "
            f"{fmt_int(perdidos)} abandonaram — apenas {fmt_pct(ratio_pct(fim, base))} avançaram. "
            "Vale priorizar essa etapa para destravar conversão."
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

    # --- Página 3: taxas de conversão + leituras ---
    conv_visitas_vendas = ratio_pct(vendas, visitas)
    conv_visitas_carrinhos = ratio_pct(t["carrinhos"], visitas)
    conv_checkouts_vendas = ratio_pct(vendas, t["checkout_iniciado"])

    r.section("Taxas de conversão (painel NuvemShop)")
    r.conversion_cards(
        [
            (fmt_pct(conv_visitas_vendas), "Visitas a vendas", "Conversão geral do site"),
            (fmt_pct(conv_visitas_carrinhos), "Visitas a carrinhos", "Intenção de compra gerada"),
            (fmt_pct(conv_checkouts_vendas), "Checkouts a vendas", "Eficiência do checkout"),
        ]
    )
    r.note(
        "As taxas acima são consolidadas a partir dos relatórios da NuvemShop e podem usar "
        "bases (sessões únicas) distintas das contagens absolutas do funil — por isso pode "
        "haver pequena divergência em relação aos percentuais calculados sobre as visitas."
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
        ]
    )

    r.page_break()

    # --- Página 4: recomendações + rodapé ---
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
            (
                "Acompanhar a série ao longo do tempo.",
                "Com amostras pequenas os percentuais variam bastante; só a série de vários períodos separa tendência de ruído.",
            ),
        ],
        accent=PURPLE,
    )

    r.footer_note(
        f"Relatório interno · {empresa.nome} — Loja virtual (NuvemShop)",
        f"Gerado a partir do painel “Visão geral” · {agora.strftime('%d/%m/%Y %H:%M')}",
    )

    return r.gerar()
