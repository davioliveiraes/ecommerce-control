"""Geração do PDF de relatório do catálogo (layout rico, paleta preto e branco)."""

from collections import Counter
from typing import Optional

from django.db.models import Q
from django.utils import timezone
from reportlab.lib import colors

from accounts.models import Empresa
from catalog.models import Marca, Subcategoria, Variacao

from .report_design import RichReport, ratio_pct

# Paleta monocromática — segue o padrão preto/branco do painel
PRETO = colors.HexColor("#111111")
PRETO_BANNER = colors.HexColor("#0A0A0A")
CINZA_BANNER = colors.HexColor("#2E2E2E")
CINZA_BARRA = colors.HexColor("#9CA3AF")


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

# Largura relativa e alinhamento de cada coluna na tabela de detalhamento
LAYOUT_COLUNAS = {
    "sku": (1.6, "L"),
    "produto_descricao_site": (3.0, "L"),
    "produto_descricao_gestaoclick": (3.0, "L"),
    "variacao": (2.0, "L"),
    "marca": (1.2, "L"),
    "subcategoria": (1.5, "L"),
    "custo": (1.0, "R"),
    "preco_loja": (1.0, "R"),
    "preco_site": (1.0, "R"),
    "preco_promocional": (1.1, "R"),
    "margem_percentual": (1.0, "R"),
    "margem_promocional_percentual": (1.2, "R"),
    "status_nuvemshop": (1.3, "L"),
    "status_integracao": (1.3, "L"),
}


def gerar_relatorio_catalogo(
    empresa: Empresa,
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

    qs = Variacao.objects.select_related(
        "produto__marca", "produto__subcategoria"
    ).filter(produto__empresa=empresa)
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

    filtros = [("Status", "Ativos + inativos" if incluir_inativos else "Apenas ativos")]
    if apenas_promocional:
        filtros.append(("Promoção", "Apenas variações com preço promocional"))
    if marca_id is not None:
        marca = Marca.objects.filter(id=marca_id, empresa=empresa).first()
        if marca:
            filtros.append(("Marca", marca.nome))
    if subcategoria_id is not None:
        subcategoria = Subcategoria.objects.filter(
            id=subcategoria_id, empresa=empresa
        ).first()
        if subcategoria:
            filtros.append(("Subcategoria", subcategoria.nome))
    if busca:
        filtros.append(("Busca", busca))
    filtros.append(
        (
            "Colunas no relatório",
            ", ".join(COLUNAS_DISPONIVEIS[coluna][0] for coluna in colunas_validas),
        )
    )

    variacoes = list(qs)

    # --- agregados ---------------------------------------------------------
    total = len(variacoes)
    produtos = {variacao.produto_id for variacao in variacoes}
    ativos = sum(1 for variacao in variacoes if variacao.ativo)
    inativas = total - ativos
    precos_site = [v.preco_site for v in variacoes if v.preco_site is not None]
    sem_preco_site = total - len(precos_site)
    margens = [v.margem_percentual for v in variacoes if v.margem_percentual is not None]
    preco_medio = sum(precos_site) / len(precos_site) if precos_site else None
    margem_media = sum(margens) / len(margens) if margens else None
    em_promocao = sum(1 for v in variacoes if v.preco_promocional is not None)
    nuvemshop_ativo = sum(1 for v in variacoes if v.status_nuvemshop == "ATIVO")
    integracao_ativa = sum(1 for v in variacoes if v.status_integracao == "ATIVO")
    integracao_inativa = total - integracao_ativa
    marcas = Counter(
        v.produto.marca.nome if v.produto.marca else "Sem marca" for v in variacoes
    )
    subcategorias = Counter(
        v.produto.subcategoria.nome if v.produto.subcategoria else "Sem subcategoria"
        for v in variacoes
    )

    # --- montagem ------------------------------------------------------------
    r = RichReport(accent=PRETO, banner_bg=PRETO_BANNER, banner_soft=CINZA_BANNER)
    agora = timezone.localtime()
    r.set_page_footer(f"Controle Interno · {empresa.nome}")

    r.header_band(
        wordmark=empresa.nome,
        kicker=f"{empresa.nome} Ecommerce Control · Relatório de desempenho".upper(),
        title="Catálogo",
        subtitle="Posição do catálogo: disponibilidade, cobertura de preços "
        "e agrupamentos comerciais.",
        badge=f"CATÁLOGO · {agora.strftime('%d/%m/%Y')}",
        meta_lines=[
            "Módulo 01 · Catálogo",
            f"Gerado em: <b>{agora.strftime('%d/%m/%Y')} às {agora.strftime('%H:%M')}</b>",
        ],
    )

    r.section("Visão geral")
    r.box_text(
        f"Este relatório apresenta a posição do catálogo {empresa.nome} no recorte "
        "selecionado, com leitura de disponibilidade, cobertura de preços e "
        "agrupamentos comerciais antes da listagem operacional."
    )

    r.section("Filtros aplicados")
    r.filters_box(filtros)

    r.section("Indicadores do catálogo")
    r.kpi_cards(
        [
            ("Variações", f"{total}", PRETO),
            ("Produtos", f"{len(produtos)}", PRETO),
            ("Ativas", f"{ativos}", PRETO),
            ("Preço site médio", format_brl(preco_medio), PRETO),
        ]
    )
    r.stat_cards(
        [
            ("Margem média", format_percent(margem_media)),
            ("Com preço site", f"{len(precos_site)}"),
            ("Com preço promocional", f"{em_promocao}"),
            ("Marcas", f"{len(marcas)}"),
            ("Subcategorias", f"{len(subcategorias)}"),
        ]
    )

    r.section("Distribuição de status")
    r.two_bar_panels(
        (
            "Status NuvemShop",
            [
                ("Ativo", nuvemshop_ativo, ratio_pct(nuvemshop_ativo, total) / 100, PRETO),
                ("Inativo", total - nuvemshop_ativo, ratio_pct(total - nuvemshop_ativo, total) / 100, CINZA_BARRA),
            ],
        ),
        (
            "Status de integração",
            [
                ("Ativo", integracao_ativa, ratio_pct(integracao_ativa, total) / 100, PRETO),
                ("Inativo", integracao_inativa, ratio_pct(integracao_inativa, total) / 100, CINZA_BARRA),
            ],
        ),
    )

    if not variacoes:
        r.note("Nenhuma variação encontrada no recorte selecionado.", accent=PRETO)
        return r.gerar()

    r.page_break()

    # --- página 2: agrupamentos, leituras e recomendações ---------------------
    r.section("Principais agrupamentos")
    r.two_panels(
        "Por subcategoria",
        [(label, f"{valor}") for label, valor in subcategorias.most_common(5)],
        "Por marca",
        [(label, f"{valor}") for label, valor in marcas.most_common(5)],
    )

    marca_lider, marca_lider_qtd = marcas.most_common(1)[0]
    pct_marca_lider = ratio_pct(marca_lider_qtd, total)
    concentracao = (
        "Concentração alta aumenta a dependência de poucos fornecedores."
        if pct_marca_lider >= 50
        else "Distribuição relativamente equilibrada entre marcas."
    )

    leituras = [
        (
            "Tamanho e disponibilidade.",
            f"{total} variações em {len(produtos)} produtos no recorte, {ativos} ativas "
            f"({format_percent(ratio_pct(ativos, total))}). {inativas} estão inativas.",
        ),
        (
            "Cobertura de preço de site.",
            f"{len(precos_site)} variações com preço de site definido "
            f"({format_percent(ratio_pct(len(precos_site), total))}); "
            + (
                f"{sem_preco_site} ainda sem preço — pontos cegos para a vitrine."
                if sem_preco_site
                else "nenhuma pendência de preço."
            ),
        ),
        (
            "Preço e margem médios.",
            f"Preço de site médio de {format_brl(preco_medio)} e margem média de "
            f"{format_percent(margem_media)} entre as variações com dados.",
        ),
        (
            "Concentração por marca.",
            f"'{marca_lider}' lidera com {marca_lider_qtd} variações "
            f"({format_percent(pct_marca_lider)} do recorte). {concentracao}",
        ),
        (
            "Integração GestãoClick–NuvemShop.",
            (
                f"{integracao_inativa} variações com integração inativa "
                f"({format_percent(ratio_pct(integracao_inativa, total))}) — risco de "
                "divergência de estoque/preço entre os sistemas."
                if integracao_inativa
                else "Todas as variações com integração ativa entre os sistemas."
            ),
        ),
        (
            "Promoções ativas.",
            (
                f"{em_promocao} variações com preço promocional "
                f"({format_percent(ratio_pct(em_promocao, total))})."
                if em_promocao
                else "Nenhuma variação com preço promocional no recorte."
            ),
        ),
    ]

    r.section("Principais leituras")
    r.numbered_list(leituras, accent=PRETO)

    recomendacoes = []
    if sem_preco_site:
        recomendacoes.append(
            (
                "Completar preços de site faltantes.",
                f"{sem_preco_site} variações sem preço de site não aparecem corretamente "
                "na vitrine. Priorizar o preenchimento para não perder exposição.",
            )
        )
    if integracao_inativa:
        recomendacoes.append(
            (
                "Reativar integrações pendentes.",
                f"Verificar as {integracao_inativa} variações com integração inativa para "
                "evitar divergências entre GestãoClick e NuvemShop.",
            )
        )
    if inativas:
        recomendacoes.append(
            (
                "Revisar variações inativas.",
                f"{inativas} variações inativas no recorte — confirmar se é ruptura de "
                "estoque ou descontinuação e ajustar o catálogo.",
            )
        )
    recomendacoes.append(
        (
            "Padronizar descrições.",
            "Manter descrições de site e GestãoClick alinhadas facilita conferência, "
            "busca interna e geração de relatórios.",
        )
    )

    r.section("Recomendações")
    r.numbered_list(recomendacoes[:3], accent=PRETO)

    r.page_break()

    # --- página 3+: detalhamento ----------------------------------------------
    headers = [COLUNAS_DISPONIVEIS[coluna][0] for coluna in colunas_validas]
    linhas = [
        [str(COLUNAS_DISPONIVEIS[coluna][1](variacao)) for coluna in colunas_validas]
        for variacao in variacoes
    ]
    fracs = [LAYOUT_COLUNAS[coluna][0] for coluna in colunas_validas]
    aligns = [LAYOUT_COLUNAS[coluna][1] for coluna in colunas_validas]

    r.section("Detalhamento das variações")
    r.data_table(headers, linhas, fracs=fracs, aligns=aligns)
    r.totals_line(
        [
            ("Total de registros", f"{total}"),
            ("Amostra exibida", f"{len(linhas)}"),
        ]
    )

    return r.gerar()
