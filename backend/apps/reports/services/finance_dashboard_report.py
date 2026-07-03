"""Relatório PDF do dashboard financeiro no mesmo layout rico da Visão Geral."""

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from django.utils import timezone

from finance.models import LancamentoFinanceiro

from .report_design import (
    GREEN,
    NAVY,
    ORANGE,
    PURPLE,
    RichReport,
    fmt_brl,
    fmt_int,
    fmt_pct,
    ratio_pct,
)

_MESES = {
    "01": "jan", "02": "fev", "03": "mar", "04": "abr", "05": "mai", "06": "jun",
    "07": "jul", "08": "ago", "09": "set", "10": "out", "11": "nov", "12": "dez",
}


def _label_periodo(data_inicio: Optional[date], data_fim: Optional[date]) -> str:
    if data_inicio and data_fim:
        return f"{data_inicio.strftime('%d/%m/%Y')} – {data_fim.strftime('%d/%m/%Y')}"
    if data_inicio:
        return f"a partir de {data_inicio.strftime('%d/%m/%Y')}"
    if data_fim:
        return f"até {data_fim.strftime('%d/%m/%Y')}"
    return "Todo o período"


def _mes_legivel(chave: str) -> str:
    # chave no formato "YYYY-MM"
    ano, mes = chave.split("-")
    return f"{_MESES.get(mes, mes)}/{ano[2:]}"


def gerar_relatorio_finance_dashboard(
    empresa,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    categoria_id: Optional[int] = None,
) -> bytes:
    qs = LancamentoFinanceiro.objects.filter(
        ativo=True, status="PAGO", empresa=empresa
    ).select_related("categoria")
    if data_inicio is not None:
        qs = qs.filter(data_lancamento__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_lancamento__lte=data_fim)
    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)
    lancamentos = list(qs)

    receitas = sum((l.valor for l in lancamentos if l.tipo == "RECEITA"), Decimal("0"))
    custos = sum((l.valor for l in lancamentos if l.tipo == "CUSTO"), Decimal("0"))
    despesas = sum((l.valor for l in lancamentos if l.tipo == "DESPESA"), Decimal("0"))
    resultado = receitas - custos - despesas
    margem = ratio_pct(float(resultado), float(receitas)) if receitas else 0.0

    serie = defaultdict(lambda: {"receita": Decimal("0"), "saida": Decimal("0")})
    por_categoria_receita = defaultdict(lambda: Decimal("0"))
    por_categoria_saida = defaultdict(lambda: Decimal("0"))
    por_forma = defaultdict(lambda: Decimal("0"))
    for l in lancamentos:
        chave = l.data_lancamento.strftime("%Y-%m")
        cat = l.categoria.nome if l.categoria else "Sem categoria"
        if l.tipo == "RECEITA":
            serie[chave]["receita"] += l.valor
            por_categoria_receita[cat] += l.valor
            forma = l.get_forma_pagamento_display() if l.forma_pagamento else "Não informado"
            por_forma[forma] += l.valor
        else:
            serie[chave]["saida"] += l.valor
            por_categoria_saida[cat] += l.valor

    meses = sorted(serie.items())

    r = RichReport()
    agora = timezone.localtime()

    # --- Página 1: cabeçalho + KPIs ---
    r.header_band(
        wordmark=empresa.nome,
        kicker="RELATÓRIO FINANCEIRO — CONTROLE INTERNO",
        title="Resultado financeiro",
        subtitle="Consolidação de receitas, custos e despesas pagos no período, "
        "com evolução mensal e composição por categoria.",
        badge=f"PERÍODO · {len(lancamentos)} LANÇAMENTO(S)",
        meta_lines=[
            f"Período: <b>{_label_periodo(data_inicio, data_fim)}</b>",
            f"Gerado em: <b>{agora.strftime('%d/%m/%Y %H:%M')}</b>",
            "Base: lançamentos pagos",
        ],
    )

    if not lancamentos:
        r.section("Sem dados no período")
        r.note(
            "Nenhum lançamento pago foi encontrado para o intervalo selecionado. "
            "Ajuste o período ou registre lançamentos para gerar este relatório."
        )
        return r.gerar()

    r.section("Indicadores do período")
    r.kpi_cards(
        [
            ("Receita", fmt_brl(receitas), GREEN),
            ("Custos", fmt_brl(custos), ORANGE),
            ("Despesas", fmt_brl(despesas), ORANGE),
            ("Resultado", fmt_brl(resultado), NAVY if resultado >= 0 else ORANGE),
        ]
    )

    r.page_break()

    # --- Página 2: evolução mensal + composição ---
    r.section("Evolução mensal — receita")
    r.bars(
        [
            (_mes_legivel(mes), float(v["receita"]), fmt_brl(v["receita"]), GREEN)
            for mes, v in meses
        ]
    )

    if meses:
        melhor = max(meses, key=lambda m: m[1]["receita"])
        pior = min(meses, key=lambda m: m[1]["receita"])
        r.callout(
            f"Melhor mês de receita: <b>{_mes_legivel(melhor[0])}</b> com {fmt_brl(melhor[1]['receita'])}. "
            f"Menor: <b>{_mes_legivel(pior[0])}</b> com {fmt_brl(pior[1]['receita'])}. "
            "Compare com investimento de marketing e sazonalidade para entender as variações.",
            accent=GREEN,
        )

    top_receitas = sorted(por_categoria_receita.items(), key=lambda x: x[1], reverse=True)[:5]
    top_saidas = sorted(por_categoria_saida.items(), key=lambda x: x[1], reverse=True)[:5]
    r.section("Composição por categoria")
    r.two_panels(
        "Receitas por categoria",
        [(nome, fmt_brl(v)) for nome, v in top_receitas] or [("Sem registros", fmt_brl(0))],
        "Saídas por categoria (custos + despesas)",
        [(nome, fmt_brl(v)) for nome, v in top_saidas] or [("Sem registros", fmt_brl(0))],
    )

    r.page_break()

    # --- Página 3: formas de pagamento + leituras ---
    total_forma = sum(por_forma.values()) or Decimal("1")
    formas_ordenadas = sorted(por_forma.items(), key=lambda x: x[1], reverse=True)[:3]
    r.section("Formas de pagamento (receita recebida)")
    if formas_ordenadas:
        r.conversion_cards(
            [
                (
                    fmt_pct(ratio_pct(float(v), float(total_forma))),
                    nome,
                    fmt_brl(v),
                )
                for nome, v in formas_ordenadas
            ]
        )
    r.note(
        "Toda a receita entra pela conta de pagamentos da NuvemShop (NuvemPago). "
        "A divisão acima é por forma de pagamento escolhida pelo cliente (Pix, cartão, boleto)."
    )

    qtd_pagos = len(lancamentos)
    r.section("Principais leituras")
    r.numbered_list(
        [
            (
                "Resultado do período.",
                f"Receita de {fmt_brl(receitas)} contra {fmt_brl(custos + despesas)} de saídas, "
                f"resultando em {fmt_brl(resultado)} (margem de {fmt_pct(margem)}).",
            ),
            (
                "Peso das saídas.",
                f"Custos somam {fmt_brl(custos)} e despesas {fmt_brl(despesas)}. "
                "Acompanhar as categorias de maior saída ajuda a proteger a margem.",
            ),
            (
                "Distribuição temporal.",
                f"Foram {qtd_pagos} lançamentos pagos distribuídos em {len(meses)} mês(es) do período.",
            ),
        ]
    )

    r.page_break()

    # --- Página 4: recomendações + rodapé ---
    r.section("Recomendações")
    r.numbered_list(
        [
            (
                "Monitorar a margem mês a mês.",
                "Acompanhe a relação receita × saídas para identificar meses fora do padrão cedo.",
            ),
            (
                "Revisar as maiores categorias de saída.",
                "Concentre a negociação e o corte de custos onde o gasto é mais relevante.",
            ),
            (
                "Conciliar com o painel de pagamentos.",
                "Cruze a receita recebida com os repasses da conta NuvemShop para garantir consistência.",
            ),
        ],
        accent=PURPLE,
    )

    r.footer_note(
        f"Relatório interno · {empresa.nome} — Loja virtual (NuvemShop)",
        f"Gerado a partir do painel “Financeiro” · {agora.strftime('%d/%m/%Y %H:%M')}",
    )

    return r.gerar()
