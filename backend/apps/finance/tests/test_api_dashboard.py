from datetime import date
from decimal import Decimal

from django.test import TestCase

from finance.models import CategoriaFinanceira, LancamentoFinanceiro
from config.testing import create_authenticated_client


class DashboardAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.cat_frete = CategoriaFinanceira.objects.create(empresa=self.user.empresa, 
            nome="Frete", slug="frete"
        )
        self.cat_mkt = CategoriaFinanceira.objects.create(empresa=self.user.empresa, 
            nome="Marketing", slug="mkt"
        )
        self.cat_vendas, _ = CategoriaFinanceira.objects.get_or_create(
            slug="vendas-nuvemshop",
            defaults={"nome": "Vendas NuvemShop"},
        )

        # Maio: 100 receita, 30 custo, 20 despesa = lucro 50
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="Venda 1", tipo="RECEITA", valor=Decimal("100"),
            categoria=self.cat_vendas,
            data_lancamento=date(2026, 5, 1), status="PAGO",
            forma_pagamento="PIX", meio_pagamento="NUVEMPAGO",
            quantidade_parcelas=1, quantidade_vendas=2,
            fonte_trafego="Instagram",
        )
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="Estoque", tipo="CUSTO", categoria=self.cat_frete,
            valor=Decimal("30"),
            data_lancamento=date(2026, 5, 5), status="PAGO",
        )
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="Ads", tipo="DESPESA", categoria=self.cat_mkt,
            valor=Decimal("20"),
            data_lancamento=date(2026, 5, 10), status="PAGO",
        )
        # Pendente — não conta por padrão
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
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

        receitas = data["receitas_por_categoria"]
        self.assertEqual(len(receitas), 1)
        self.assertEqual(receitas[0]["categoria_nome"], "Vendas NuvemShop")
        self.assertEqual(Decimal(receitas[0]["valor"]), Decimal("100"))

    def test_metricas_pagamento(self):
        response = self.client.get("/finance/dashboard/")
        data = response.json()

        forma = data["receita_vendas_por_forma_pagamento"][0]
        self.assertEqual(forma["chave"], "PIX")
        self.assertEqual(forma["nome"], "Pix")
        self.assertEqual(Decimal(forma["receita"]), Decimal("100"))
        self.assertEqual(forma["vendas"], 2)

        meio = data["receita_vendas_por_meio_pagamento"][0]
        self.assertEqual(meio["chave"], "NUVEMPAGO")
        self.assertEqual(meio["nome"], "NuvemPago")

        parcelas = data["receita_vendas_por_parcelas"][0]
        self.assertEqual(parcelas["chave"], "1")
        self.assertEqual(parcelas["nome"], "1x")

    def test_filtra_por_categoria(self):
        response = self.client.get(
            f"/finance/dashboard/?categoria_id={self.cat_mkt.id}"
        )
        data = response.json()

        self.assertEqual(Decimal(data["kpis"]["receita_total"]), Decimal("0"))
        self.assertEqual(Decimal(data["kpis"]["custo_total"]), Decimal("0"))
        self.assertEqual(Decimal(data["kpis"]["despesa_total"]), Decimal("20"))
        self.assertEqual(data["despesas_por_categoria"][0]["categoria_nome"], "Marketing")
        self.assertEqual(data["receita_vendas_por_forma_pagamento"], [])

    def test_filtra_por_tipo(self):
        response = self.client.get("/finance/dashboard/?tipo=RECEITA")
        data = response.json()

        self.assertEqual(Decimal(data["kpis"]["receita_total"]), Decimal("100"))
        self.assertEqual(Decimal(data["kpis"]["despesa_total"]), Decimal("0"))
        self.assertEqual(data["despesas_por_categoria"], [])
        self.assertEqual(
            data["receitas_por_categoria"][0]["categoria_nome"],
            "Vendas NuvemShop",
        )
