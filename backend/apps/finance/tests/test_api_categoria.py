from django.test import TestCase

from finance.models import CategoriaFinanceira
from config.testing import create_authenticated_client


class CategoriaAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()

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
        CategoriaFinanceira.objects.create(empresa=self.user.empresa, nome="A", slug="a")
        CategoriaFinanceira.objects.create(empresa=self.user.empresa, nome="I", slug="i", ativo=False)

        response = self.client.get("/finance/categorias/")
        nomes = [c["nome"] for c in response.json()]
        self.assertIn("A", nomes)
        self.assertNotIn("I", nomes)
