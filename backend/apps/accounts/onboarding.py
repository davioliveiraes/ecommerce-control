"""Dados iniciais criados para cada empresa recém-cadastrada."""

from .models import Empresa

# Slugs fixos: o frontend usa alguns deles para inferir o tipo do lançamento
# (vendas-nuvemshop → RECEITA, embalagens-frete → CUSTO, demais → DESPESA).
CATEGORIAS_FINANCEIRAS_PADRAO = [
    ("Vendas NuvemShop", "vendas-nuvemshop", "#0A0A0A"),
    ("Plano NuvemShop", "nuvemshop-plano", "#262626"),
    ("Hospedagem & Domínio", "hospedagem-dominio", "#404040"),
    ("E-mail Profissional", "email-profissional", "#525252"),
    ("Equipe Ecommerce", "equipe-ecommerce", "#737373"),
    ("Marketing & Tráfego", "marketing-trafego", "#8A8A8A"),
    ("Taxas de Meios de Pagamento", "taxas-meios-pagamento", "#A3A3A3"),
    ("Embalagens & Frete", "embalagens-frete", "#BFBFBF"),
]


def semear_dados_iniciais(empresa: Empresa) -> None:
    from finance.models import CategoriaFinanceira

    CategoriaFinanceira.objects.bulk_create(
        [
            CategoriaFinanceira(
                empresa=empresa, nome=nome, slug=slug, cor_hex=cor_hex
            )
            for nome, slug, cor_hex in CATEGORIAS_FINANCEIRAS_PADRAO
        ]
    )
