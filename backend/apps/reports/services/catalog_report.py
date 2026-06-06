"""Geração do PDF de relatório do catálogo."""

from collections import Counter
from typing import Optional

from django.db.models import Q

from catalog.models import Marca, Subcategoria, Variacao

from .pdf_base import RelatorioPDF


def format_brl(valor) -> str:
    if valor is None:
        return "-"
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def format_percent(valor) -> str:
    if valor is None:
        return "-"
    return f"{valor:.1f}%".replace(".", ",")


STATUS_LABEL = {"ATIVO": "Ativo", "INATIVO": "Inativo"}


def format_status(valor) -> str:
    return STATUS_LABEL.get(valor or "", valor or "-")


COLUNAS_DISPONIVEIS = {
    "sku": ("SKU", lambda v: v.sku_nuvemshop or "-"),
    "produto_descricao_site": (
        "Produto (Site)",
        lambda v: v.produto.descricao_produto_site or "-",
    ),
    "produto_descricao_gestaoclick": (
        "Produto (GestãoClick)",
        lambda v: v.produto.descricao_produto_gestaoclick or "-",
    ),
    "variacao": ("Variação", lambda v: v.descricao or "-"),
    "marca": ("Marca", lambda v: v.produto.marca.nome if v.produto.marca else "-"),
    "subcategoria": (
        "Subcategoria",
        lambda v: v.produto.subcategoria.nome if v.produto.subcategoria else "-",
    ),
    "custo": ("Custo", lambda v: format_brl(v.custo)),
    "preco_loja": ("Preço Loja", lambda v: format_brl(v.preco_loja)),
    "preco_site": ("Preço Site", lambda v: format_brl(v.preco_site)),
    "preco_promocional": ("Preço Promo", lambda v: format_brl(v.preco_promocional)),
    "margem_percentual": ("Margem %", lambda v: format_percent(v.margem_percentual)),
    "margem_promocional_percentual": (
        "Margem Promo %",
        lambda v: format_percent(v.margem_promocional_percentual),
    ),
    "status_nuvemshop": (
        "Status NuvemShop",
        lambda v: format_status(v.status_nuvemshop),
    ),
    "status_integracao": (
        "Status Integração",
        lambda v: format_status(v.status_integracao),
    ),
}

COLUNAS_PADRAO = ["sku", "produto_descricao_site", "variacao", "preco_site"]


def gerar_relatorio_catalogo(
    colunas: list[str],
    incluir_inativos: bool = False,
    marca_id: Optional[int] = None,
    subcategoria_id: Optional[int] = None,
    busca: str = "",
    apenas_promocional: bool = False,
) -> bytes:
    colunas_validas = [coluna for coluna in colunas if coluna in COLUNAS_DISPONIVEIS]
    if not colunas_validas:
        colunas_validas = COLUNAS_PADRAO

    qs = Variacao.objects.select_related("produto__marca", "produto__subcategoria")
    if not incluir_inativos:
        qs = qs.filter(ativo=True)
    if marca_id is not None:
        qs = qs.filter(produto__marca_id=marca_id)
    if subcategoria_id is not None:
        qs = qs.filter(produto__subcategoria_id=subcategoria_id)
    if apenas_promocional:
        qs = qs.filter(preco_promocional__isnull=False)
    if busca:
        qs = qs.filter(
            Q(sku_nuvemshop__icontains=busca)
            | Q(descricao__icontains=busca)
            | Q(produto__nome_site__icontains=busca)
            | Q(produto__descricao_produto_site__icontains=busca)
            | Q(produto__descricao_produto_gestaoclick__icontains=busca)
        )
    qs = qs.order_by("produto__descricao_produto_site", "produto__nome_site", "descricao")

    filtros = {"Status": "Ativos + inativos" if incluir_inativos else "Apenas ativos"}
    if apenas_promocional:
        filtros["Promoção"] = "Apenas variações com preço promocional"
    if marca_id is not None:
        marca = Marca.objects.filter(id=marca_id).first()
        if marca:
            filtros["Marca"] = marca.nome
    if subcategoria_id is not None:
        subcategoria = Subcategoria.objects.filter(id=subcategoria_id).first()
        if subcategoria:
            filtros["Subcategoria"] = subcategoria.nome
    if busca:
        filtros["Busca"] = busca

    variacoes = list(qs)
    headers = [COLUNAS_DISPONIVEIS[coluna][0] for coluna in colunas_validas]
    linhas = [
        [str(COLUNAS_DISPONIVEIS[coluna][1](variacao)) for coluna in colunas_validas]
        for variacao in variacoes
    ]

    total = len(variacoes)
    produtos = {variacao.produto_id for variacao in variacoes}
    ativos = sum(1 for variacao in variacoes if variacao.ativo)
    com_preco_site = [
        variacao.preco_site for variacao in variacoes if variacao.preco_site is not None
    ]
    margens = [
        variacao.margem_percentual
        for variacao in variacoes
        if variacao.margem_percentual is not None
    ]
    preco_medio = sum(com_preco_site) / len(com_preco_site) if com_preco_site else None
    margem_media = sum(margens) / len(margens) if margens else None
    status_nuvemshop = Counter(
        format_status(variacao.status_nuvemshop) for variacao in variacoes
    )
    status_integracao = Counter(
        format_status(variacao.status_integracao) for variacao in variacoes
    )
    em_promocao = sum(1 for v in variacoes if v.preco_promocional is not None)
    precos_promo = [v.preco_promocional for v in variacoes if v.preco_promocional is not None]
    promo_medio = sum(precos_promo) / len(precos_promo) if precos_promo else None
    marcas = Counter(
        variacao.produto.marca.nome if variacao.produto.marca else "Sem marca"
        for variacao in variacoes
    )
    subcategorias = Counter(
        variacao.produto.subcategoria.nome
        if variacao.produto.subcategoria
        else "Sem subcategoria"
        for variacao in variacoes
    )

    pdf = RelatorioPDF(subtitulo="Relatório de Catálogo", orientacao="landscape")
    pdf.adicionar_secao("Visão geral")
    pdf.adicionar_texto(
        "Este relatório apresenta a posição do catálogo no recorte "
        "selecionado, com leitura de disponibilidade, cobertura de preços e "
        "agrupamentos comerciais antes da listagem operacional."
    )
    kpis = [
        ("Variações", f"{total}"),
        ("Produtos", f"{len(produtos)}"),
        ("Ativas", f"{ativos}"),
        ("Preço site médio", format_brl(preco_medio)),
        ("Margem média", format_percent(margem_media)),
        ("Em promoção", f"{em_promocao}"),
        ("Marcas", f"{len(marcas)}"),
        ("Subcategorias", f"{len(subcategorias)}"),
    ]
    if apenas_promocional:
        kpis[5] = ("Preço promo médio", format_brl(promo_medio))
    pdf.adicionar_kpis(kpis)
    pdf.adicionar_filtros(filtros)
    pdf.adicionar_grafico_barras(
        "Status NuvemShop",
        [(label, float(valor)) for label, valor in status_nuvemshop.most_common()],
    )
    pdf.adicionar_grafico_barras(
        "Status de integração",
        [(label, float(valor)) for label, valor in status_integracao.most_common()],
    )
    pdf.adicionar_secao("Principais agrupamentos")
    pdf.adicionar_tabela(
        ["Subcategoria", "Variações"],
        [[label, str(valor)] for label, valor in subcategorias.most_common(8)]
        or [["Sem registros", "0"]],
    )
    pdf.adicionar_tabela(
        ["Marca", "Variações"],
        [[label, str(valor)] for label, valor in marcas.most_common(8)]
        or [["Sem registros", "0"]],
    )
    pdf.adicionar_secao("Detalhamento")
    pdf.adicionar_tabela(headers, linhas or [["Sem registros"] + [""] * (len(headers) - 1)])
    pdf.adicionar_totais([f"Total de registros: {len(variacoes)}"])
    return pdf.gerar()
