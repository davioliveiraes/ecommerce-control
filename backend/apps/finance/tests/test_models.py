from datetime import date
from decimal import Decimal

from django.test import TestCase

from finance.models import CategoriaFinanceira, LancamentoFinanceiro


class CategoriaFinanceiraTestCase(TestCase):
    def test_criar(self):
        cat = CategoriaFinanceira.objects.create(nome="Frete", slug="frete")
        self.assertEqual(str(cat), "Frete")
        self.assertTrue(cat.ativo)

    def test_soft_delete(self):
        cat = CategoriaFinanceira.objects.create(nome="X", slug="x")
        cat.delete()
        cat.refresh_from_db()
        self.assertFalse(cat.ativo)


class LancamentoFinanceiroTestCase(TestCase):
    def setUp(self):
        self.categoria = CategoriaFinanceira.objects.create(
            nome="Marketing", slug="marketing"
        )

    def test_criar(self):
        l = LancamentoFinanceiro.objects.create(
            descricao="Google Ads",
            tipo="DESPESA",
            categoria=self.categoria,
            valor=Decimal("250.00"),
            data_lancamento=date(2026, 5, 1),
        )
        self.assertEqual(l.status, "PENDENTE")  # default
        self.assertIn("Google Ads", str(l))

    def test_sem_categoria(self):
        l = LancamentoFinanceiro.objects.create(
            descricao="X",
            tipo="RECEITA",
            valor=Decimal("100.00"),
            data_lancamento=date(2026, 5, 1),
        )
        self.assertIsNone(l.categoria)
