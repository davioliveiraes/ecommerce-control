from datetime import date
from decimal import Decimal

from django.test import TestCase

from finance.models import CategoriaFinanceira, LancamentoFinanceiro
from config.testing import create_authenticated_client


class LancamentoAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.cat = CategoriaFinanceira.objects.create(empresa=self.user.empresa, nome="Frete", slug="frete")

    def test_create_lancamento(self):
        payload = {
            "descricao": "Frete Correios",
            "tipo": "DESPESA",
            "categoria_id": self.cat.id,
            "valor": "45.50",
            "data_lancamento": "2026-05-10",
            "status": "PAGO",
        }
        response = self.client.post("/finance/lancamentos/", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["descricao"], "Frete Correios")
        self.assertEqual(data["categoria_nome"], "Frete")
        self.assertEqual(data["status"], "PAGO")

    def test_filtros(self):
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="A", tipo="DESPESA", valor=Decimal("10"),
            data_lancamento=date(2026, 5, 1), status="PAGO",
        )
        LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="B", tipo="RECEITA", valor=Decimal("20"),
            data_lancamento=date(2026, 5, 1), status="PENDENTE",
        )

        response = self.client.get("/finance/lancamentos/?tipo=DESPESA")
        self.assertEqual(len(response.json()), 1)

        response = self.client.get("/finance/lancamentos/?status=PAGO")
        self.assertEqual(len(response.json()), 1)

    def test_marcar_pago(self):
        l = LancamentoFinanceiro.objects.create(empresa=self.user.empresa, 
            descricao="X", tipo="DESPESA", valor=Decimal("10"),
            data_lancamento=date(2026, 5, 1),
        )
        self.assertEqual(l.status, "PENDENTE")
        response = self.client.post(f"/finance/lancamentos/{l.id}/marcar-pago")
        self.assertEqual(response.status_code, 200)
        l.refresh_from_db()
        self.assertEqual(l.status, "PAGO")
