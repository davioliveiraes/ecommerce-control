"""Relatório PDF das Finanças Gerais (layout rico, paleta preto e branco)."""

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from django.utils import timezone
from reportlab.lib import colors

from finance.models import CategoriaFinanceira, LancamentoFinanceiro

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

    categoria_nome = "Todas"
    if categoria_id is not None:
        categoria = CategoriaFinanceira.objects.filter(
            id=categoria_id, empresa=empresa
        ).first()
        categoria_nome = categoria.nome if categoria else f"#{categoria_id}"

    receitas = sum((l.valor for l in lancamentos if l.tipo == "RECEITA"), Decimal("0"))
    custos = sum((l.valor for l in lancamentos if l.tipo == "CUSTO"), Decimal("0"))
    despesas = sum((l.valor for l in lancamentos if l.tipo == "DESPESA"), Decimal("0"))
    saidas = custos + despesas
    resultado = receitas - saidas
    margem = ratio_pct(float(resultado), float(receitas)) if receitas else 0.0

    serie = defaultdict(
        lambda: {"receita": Decimal("0"), "custo": Decimal("0"), "despesa": Decimal("0")}
    )
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
        elif l.tipo == "CUSTO":
            serie[chave]["custo"] += l.valor
            por_categoria_saida[cat] += l.valor
        else:
            serie[chave]["despesa"] += l.valor
            por_categoria_saida[cat] += l.valor

    meses = sorted(serie.items())

    # --- montagem ------------------------------------------------------------
    r = RichReport(accent=PRETO, banner_bg=PRETO_BANNER, banner_soft=CINZA_BANNER)
    agora = timezone.localtime()
    r.set_page_footer(f"Controle Interno · {empresa.nome}")

    r.header_band(
        wordmark=empresa.nome,
        kicker=f"{empresa.nome} Ecommerce Control · Relatório financeiro".upper(),
        title="Finanças gerais",
        subtitle="Consolidação de receitas, custos e despesas pagos no período, "
        "com evolução mensal, composição por categoria e formas de pagamento.",
        badge=f"FINANÇAS GERAIS · {agora.strftime('%d/%m/%Y')}",
        meta_lines=[
            "Módulo 02 · Finanças Gerais",
            f"Período: <b>{_label_periodo(data_inicio, data_fim)}</b>",
            f"Gerado em: <b>{agora.strftime('%d/%m/%Y')} às {agora.strftime('%H:%M')}</b>",
        ],
    )

    r.section("Visão geral")
    r.box_text(
        f"Este relatório consolida o resultado financeiro da loja virtual {empresa.nome} "
        "a partir dos lançamentos pagos registrados no módulo Financeiro, com leitura da "
        "evolução mensal da receita, das maiores categorias e das formas de pagamento."
    )

    r.section("Filtros aplicados")
    r.filters_box(
        [
            ("Período", _label_periodo(data_inicio, data_fim)),
            ("Categoria", categoria_nome),
            ("Lançamentos no recorte", f"{len(lancamentos)}"),
            ("Base", "Lançamentos pagos"),
        ]
    )

    if not lancamentos:
        r.note(
            "Nenhum lançamento pago foi encontrado para o intervalo selecionado. "
            "Ajuste o período ou registre lançamentos para gerar este relatório.",
            accent=PRETO,
        )
        return r.gerar()

    r.section("Indicadores do período")
    r.kpi_cards(
        [
            ("Receita", fmt_brl(receitas), PRETO),
            ("Custos", fmt_brl(custos), PRETO),
            ("Despesas", fmt_brl(despesas), PRETO),
            ("Resultado", fmt_brl(resultado), PRETO),
        ]
    )
    r.stat_cards(
        [
            ("Margem do período", fmt_pct(margem)),
            ("Saídas totais", fmt_brl(saidas)),
            ("Lançamentos pagos", fmt_int(len(lancamentos))),
            ("Meses com movimento", fmt_int(len(meses))),
        ],
        n_por_linha=4,
    )

    r.page_break()

    # --- página 2: evolução mensal + composição ---
    r.section("Evolução mensal — receita")
    r.bars(
        [
            (_mes_legivel(mes), float(v["receita"]), fmt_brl(v["receita"]), PRETO)
            for mes, v in meses
        ]
    )

    if meses:
        melhor = max(meses, key=lambda m: m[1]["receita"])
        pior = min(meses, key=lambda m: m[1]["receita"])
        r.callout(
            f"Melhor mês de receita: {_mes_legivel(melhor[0])} com {fmt_brl(melhor[1]['receita'])}. "
            f"Menor: {_mes_legivel(pior[0])} com {fmt_brl(pior[1]['receita'])}. "
            "Compare com investimento de marketing e sazonalidade para entender as variações.",
            accent=PRETO,
            bg=SOFT_BG,
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

    # --- página 3: formas de pagamento + leituras ---
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
            ],
            accent=PRETO,
        )
    r.note(
        "Toda a receita entra pela conta de pagamentos da NuvemShop (NuvemPago). "
        "A divisão acima é por forma de pagamento escolhida pelo cliente (Pix, cartão, boleto).",
        accent=PRETO,
    )

    leituras = [
        (
            "Resultado do período.",
            f"Receita de {fmt_brl(receitas)} contra {fmt_brl(saidas)} de saídas, "
            f"resultando em {fmt_brl(resultado)} (margem de {fmt_pct(margem)}).",
        ),
        (
            "Peso das saídas.",
            f"Custos somam {fmt_brl(custos)} e despesas {fmt_brl(despesas)}. "
            "Acompanhar as categorias de maior saída ajuda a proteger a margem.",
        ),
        (
            "Distribuição temporal.",
            f"Foram {fmt_int(len(lancamentos))} lançamentos pagos distribuídos em "
            f"{fmt_int(len(meses))} mês(es) do período.",
        ),
    ]
    if formas_ordenadas:
        forma_nome, forma_valor = formas_ordenadas[0]
        leituras.append(
            (
                "Forma de pagamento principal.",
                f"{forma_nome} concentra {fmt_pct(ratio_pct(float(forma_valor), float(total_forma)))} "
                f"da receita recebida ({fmt_brl(forma_valor)}).",
            )
        )
    r.section("Principais leituras")
    r.numbered_list(leituras, accent=PRETO)

    r.page_break()

    # --- página 4: recomendações + detalhamento mensal ---
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
        accent=PRETO,
    )

    r.section("Detalhamento mensal")
    # Resumo antes da tabela: se ela quebrar de página, os totais não ficam
    # órfãos em uma página quase vazia.
    r.filters_box(
        [
            ("Meses no recorte", f"{len(meses)}"),
            ("Receita total", fmt_brl(receitas)),
            ("Resultado", fmt_brl(resultado)),
        ]
    )
    linhas = [
        [
            _mes_legivel(mes),
            fmt_brl(v["receita"]),
            fmt_brl(v["custo"]),
            fmt_brl(v["despesa"]),
            fmt_brl(v["receita"] - v["custo"] - v["despesa"]),
        ]
        for mes, v in reversed(meses)
    ]
    r.data_table(
        ["Mês", "Receita", "Custos", "Despesas", "Resultado"],
        linhas,
        fracs=[1.2, 1.3, 1.3, 1.3, 1.3],
        aligns=["L", "R", "R", "R", "R"],
    )

    return r.gerar()
