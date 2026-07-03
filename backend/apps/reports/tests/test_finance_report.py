from datetime import date
from decimal import Decimal

from django.test import TestCase

from django.contrib.auth import get_user_model

from accounts.models import Empresa
from finance.models import CategoriaFinanceira, LancamentoFinanceiro
from reports.services.finance_report import gerar_relatorio_finance


class FinanceReportTestCase(TestCase):
    def setUp(self):
        user = get_user_model().objects.create_user(username="dono")
        self.empresa = Empresa.objects.create(
            user=user, nome="Empresa Teste", cnpj="11222333000181"
        )
        self.categoria = CategoriaFinanceira.objects.create(
            empresa=self.empresa, nome="Frete", slug="frete"
        )
        LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            descricao="Venda 1",
            tipo="RECEITA",
            valor=Decimal("100"),
            data_lancamento=date(2026, 5, 1),
            status="PAGO",
        )
        LancamentoFinanceiro.objects.create(
            empresa=self.empresa,
            descricao="Despesa 1",
            tipo="DESPESA",
            categoria=self.categoria,
            valor=Decimal("30"),
            data_lancamento=date(2026, 5, 5),
            status="PAGO",
        )

    def test_gera_pdf_padrao(self):
        pdf = gerar_relatorio_finance(self.empresa, colunas=["data", "descricao", "tipo", "valor"])
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertGreater(len(pdf), 1000)

    def test_filtro_periodo(self):
        pdf = gerar_relatorio_finance(
            self.empresa,
            colunas=["data", "valor"],
            data_inicio=date(2026, 5, 1),
            data_fim=date(2026, 5, 31),
        )
        self.assertTrue(pdf.startswith(b"%PDF"))

    def test_filtro_tipo(self):
        pdf = gerar_relatorio_finance(self.empresa, colunas=["valor"], tipo="RECEITA")
        self.assertTrue(pdf.startswith(b"%PDF"))
