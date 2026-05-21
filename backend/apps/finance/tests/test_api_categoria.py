from django.test import TestCase
from ninja.testing import TestClient

from finance.models import CategoriaFinanceira
from config.api import api


class CategoriaAPITestCase(TestCase):
    def setUp(self):
        self.client = TestClient(api)

    def test_create_categoria(self):
        response = self.client.post(
            "/finance/categorias/",
            json={"nome": "Marketing Digital", "cor_hex": "#f97316"},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["slug"], "marketing-digital")
        self.assertEqual(data["cor_hex"], "#f97316")

    def test_list_so_ativas_por_padrao(self):
        CategoriaFinanceira.objects.create(nome="A", slug="a")
        CategoriaFinanceira.objects.create(nome="I", slug="i", ativo=False)

        response = self.client.get("/finance/categorias/")
        nomes = [c["nome"] for c in response.json()]
        self.assertIn("A", nomes)
        self.assertNotIn("I", nomes)
