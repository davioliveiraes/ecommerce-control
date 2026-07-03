from decimal import Decimal

from django.test import TestCase

from django.contrib.auth import get_user_model

from accounts.models import Empresa
from catalog.models import Produto, Variacao
from reports.services.catalog_report import gerar_relatorio_catalogo


class CatalogReportTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="dono")
        self.empresa = Empresa.objects.create(
            user=user, nome="Empresa Teste", cnpj="11222333000181"
        )
        self.produto = Produto.objects.create(
            empresa=self.empresa,
            descricao_produto_site="FONE TESTE",
            descricao_produto_gestaoclick="FONE TESTE GC",
        )
        Variacao.objects.create(
            produto=self.produto,
            sku_nuvemshop="SKU-1",
            descricao="USB-C",
            custo=Decimal("10.00"),
            preco_loja=Decimal("20.00"),
            preco_site=Decimal("25.00"),
        )

    def test_gera_pdf_padrao(self):
        pdf = gerar_relatorio_catalogo(self.empresa, colunas=["sku", "variacao", "preco_site"])
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)

    def test_colunas_invalidas_caem_no_default(self):
        pdf = gerar_relatorio_catalogo(self.empresa, colunas=["coluna_inexistente"])
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_filtro_busca(self):
        pdf = gerar_relatorio_catalogo(self.empresa, colunas=["sku"], busca="FONE")
        self.assertTrue(pdf.startswith(b"%PDF"))
