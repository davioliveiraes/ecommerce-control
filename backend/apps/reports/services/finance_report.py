"""Geração do PDF de relatório financeiro."""

from collections import defaultdict
from datetime import date
from decimal import Decimal
from typing import Optional

from django.db.models import Q

from finance.models import CategoriaFinanceira, LancamentoFinanceiro

from .pdf_base import RelatorioPDF


def format_brl(valor) -> str:
    if valor is None:
        return "-"
    sinal = "-" if valor < 0 else ""
    valor_abs = abs(valor)
    texto = f"R$ {valor_abs:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"{sinal}{texto}"


def format_date(valor: date | None) -> str:
    return valor.strftime("%d/%m/%Y") if valor else "-"


def valor_assinado(lancamento: LancamentoFinanceiro) -> Decimal:
    if lancamento.tipo == "RECEITA":
        return lancamento.valor
    return -lancamento.valor


COLUNAS_DISPONIVEIS = {
    "data": ("Data", lambda l: format_date(l.data_lancamento)),
    "descricao": ("Descrição", lambda l: l.descricao),
    "tipo": ("Tipo", lambda l: l.get_tipo_display()),
    "categoria": ("Categoria", lambda l: l.categoria.nome if l.categoria else "-"),
    "valor": ("Valor", lambda l: format_brl(l.valor)),
    "status": ("Status", lambda l: l.get_status_display()),
    "observacoes": ("Observações", lambda l: l.observacoes or "-"),
}

COLUNAS_PADRAO = ["data", "descricao", "tipo", "categoria", "valor", "status"]


def gerar_relatorio_finance(
    colunas: list[str],
    incluir_inativos: bool = False,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    categoria_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: str = "",
) -> bytes:
    colunas_validas = [coluna for coluna in colunas if coluna in COLUNAS_DISPONIVEIS]
    if not colunas_validas:
        colunas_validas = COLUNAS_PADRAO

    qs = LancamentoFinanceiro.objects.select_related("categoria")
    if not incluir_inativos:
        qs = qs.filter(ativo=True)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if status:
        qs = qs.filter(status=status)
    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)
    if data_inicio is not None:
        qs = qs.filter(data_lancamento__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_lancamento__lte=data_fim)
    if busca:
        qs = qs.filter(Q(descricao__icontains=busca) | Q(observacoes__icontains=busca))
    qs = qs.order_by("-data_lancamento", "-id")

    filtros = {"Status do registro": "Ativos + inativos" if incluir_inativos else "Apenas ativos"}
    if data_inicio or data_fim:
        filtros["Período"] = f"{format_date(data_inicio)} a {format_date(data_fim)}"
    if tipo:
        filtros["Tipo"] = tipo
    if status:
        filtros["Status"] = status
    if categoria_id is not None:
        categoria = CategoriaFinanceira.objects.filter(id=categoria_id).first()
        if categoria:
            filtros["Categoria"] = categoria.nome
    if busca:
        filtros["Busca"] = busca

    lancamentos = list(qs)
    receitas = sum(
        (lancamento.valor for lancamento in lancamentos if lancamento.tipo == "RECEITA"),
        Decimal("0"),
    )
    custos = sum(
        (lancamento.valor for lancamento in lancamentos if lancamento.tipo == "CUSTO"),
        Decimal("0"),
    )
    despesas = sum(
        (lancamento.valor for lancamento in lancamentos if lancamento.tipo == "DESPESA"),
        Decimal("0"),
    )
    resultado = receitas - custos - despesas

    total_por_tipo = {
        "Receitas": receitas,
        "Custos": custos,
        "Despesas": despesas,
    }
    total_por_categoria: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    resultado_mensal: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for lancamento in lancamentos:
        categoria = lancamento.categoria.nome if lancamento.categoria else "Sem categoria"
        total_por_categoria[categoria] += lancamento.valor
        mes = lancamento.data_lancamento.strftime("%m/%Y")
        resultado_mensal[mes] += valor_assinado(lancamento)

    top_categorias = sorted(
        total_por_categoria.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:8]
    meses_ordenados = sorted(
        resultado_mensal.items(),
        key=lambda item: (item[0][3:], item[0][:2]),
    )

    headers = [COLUNAS_DISPONIVEIS[coluna][0] for coluna in colunas_validas]
    linhas = [
        [str(COLUNAS_DISPONIVEIS[coluna][1](lancamento)) for coluna in colunas_validas]
        for lancamento in lancamentos
    ]

    pdf = RelatorioPDF(subtitulo="Relatório — {{COMPANY_NAME}} Finance", orientacao="landscape")
    pdf.adicionar_secao("Resumo executivo")
    pdf.adicionar_texto(
        "Este relatório consolida os lançamentos financeiros do período selecionado "
        "no dashboard, combinando leitura de resultado, composição das movimentações "
        "e detalhe operacional para conferência."
    )
    pdf.adicionar_kpis(
        [
            ("Receitas", format_brl(receitas)),
            ("Custos", format_brl(custos)),
            ("Despesas", format_brl(despesas)),
            ("Resultado", format_brl(resultado)),
            ("Lançamentos", f"{len(lancamentos)}"),
            ("Categorias", f"{len(total_por_categoria)}"),
            ("Pagos", f"{sum(1 for lancamento in lancamentos if lancamento.status == 'PAGO')}"),
            (
                "Pendentes",
                f"{sum(1 for lancamento in lancamentos if lancamento.status == 'PENDENTE')}",
            ),
        ]
    )
    pdf.adicionar_filtros(filtros)
    pdf.adicionar_grafico_barras(
        "Composição por tipo",
        [(label, float(valor)) for label, valor in total_por_tipo.items()],
    )
    pdf.adicionar_secao("Categorias com maior movimento")
    pdf.adicionar_tabela(
        ["Categoria", "Total movimentado"],
        [[label, format_brl(valor)] for label, valor in top_categorias]
        or [["Sem registros", "R$ 0,00"]],
    )
    pdf.adicionar_secao("Resultado mensal")
    pdf.adicionar_tabela(
        ["Mês", "Resultado"],
        [[mes, format_brl(valor)] for mes, valor in meses_ordenados]
        or [["Sem registros", "R$ 0,00"]],
    )
    pdf.adicionar_secao("Detalhamento")
    pdf.adicionar_tabela(headers, linhas or [["Sem registros"] + [""] * (len(headers) - 1)])
    pdf.adicionar_totais(
        [
            f"Total de registros: {len(lancamentos)}",
            f"Resultado: {format_brl(resultado)}",
        ]
    )
    return pdf.gerar()
