from datetime import date
from decimal import Decimal

from django.test import TestCase
from ninja.testing import TestClient

from finance.models import CategoriaFinanceira, LancamentoFinanceiro
from config.api import api


class DashboardAPITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)
        self.cat_frete = CategoriaFinanceira.objects.create(
            nome="Frete", slug="frete"
        )
        self.cat_mkt = CategoriaFinanceira.objects.create(
            nome="Marketing", slug="mkt"
        )

        # Maio: 100 receita, 30 custo, 20 despesa = lucro 50
        LancamentoFinanceiro.objects.create(
            descricao="Venda 1", tipo="RECEITA", valor=Decimal("100"),
            data_lancamento=date(2026, 5, 1), status="PAGO",
        )
        LancamentoFinanceiro.objects.create(
            descricao="Estoque", tipo="CUSTO", categoria=self.cat_frete,
            valor=Decimal("30"),
            data_lancamento=date(2026, 5, 5), status="PAGO",
        )
        LancamentoFinanceiro.objects.create(
            descricao="Ads", tipo="DESPESA", categoria=self.cat_mkt,
            valor=Decimal("20"),
            data_lancamento=date(2026, 5, 10), status="PAGO",
        )
        # Pendente — não conta por padrão
        LancamentoFinanceiro.objects.create(
            descricao="Futuro", tipo="DESPESA", valor=Decimal("999"),
            data_lancamento=date(2026, 5, 20), status="PENDENTE",
        )

    def test_kpis(self):
        response = self.client.get("/finance/dashboard/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(Decimal(data["kpis"]["receita_total"]), Decimal("100"))
        self.assertEqual(Decimal(data["kpis"]["custo_total"]), Decimal("30"))
        self.assertEqual(Decimal(data["kpis"]["despesa_total"]), Decimal("20"))
        self.assertEqual(Decimal(data["kpis"]["lucro"]), Decimal("50"))

    def test_incluir_pendentes(self):
        response = self.client.get("/finance/dashboard/?incluir_pendentes=true")
        data = response.json()
        self.assertEqual(
            Decimal(data["kpis"]["despesa_total"]), Decimal("1019")
        )  # 20 + 999

    def test_serie_mensal(self):
        response = self.client.get("/finance/dashboard/")
        data = response.json()
        serie = data["serie_mensal"]
        self.assertEqual(len(serie), 1)
        self.assertEqual(serie[0]["mes"], "2026-05")
        self.assertEqual(Decimal(serie[0]["receita"]), Decimal("100"))

    def test_pizza_despesas(self):
        response = self.client.get("/finance/dashboard/")
        data = response.json()
        despesas = data["despesas_por_categoria"]
        self.assertEqual(len(despesas), 1)
        self.assertEqual(despesas[0]["categoria_nome"], "Marketing")
        self.assertEqual(Decimal(despesas[0]["valor"]), Decimal("20"))
