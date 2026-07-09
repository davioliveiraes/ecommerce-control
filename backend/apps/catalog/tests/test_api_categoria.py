from django.test import TestCase

from catalog.models import Categoria, Subcategoria
from config.testing import create_authenticated_client


class CategoriaAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()

    def test_create_categoria(self):
        response = self.client.post(
            "/catalog/categorias/", json={"nome": "Acessórios"}
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nome"], "Acessórios")
        self.assertEqual(data["slug"], "acessorios")
        self.assertTrue(
            Categoria.objects.filter(
                empresa=self.user.empresa, nome="Acessórios"
            ).exists()
        )

    def test_create_categoria_existente_retorna_a_mesma(self):
        existente = Categoria.objects.create(
            empresa=self.user.empresa, nome="Áudio", slug="audio"
        )
        response = self.client.post("/catalog/categorias/", json={"nome": "áudio"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], existente.id)
        self.assertEqual(Categoria.objects.count(), 1)

    def test_create_categoria_reativa_inativa(self):
        inativa = Categoria.objects.create(
            empresa=self.user.empresa, nome="Cabos", slug="cabos", ativo=False
        )
        response = self.client.post("/catalog/categorias/", json={"nome": "Cabos"})
        self.assertEqual(response.status_code, 200)
        inativa.refresh_from_db()
        self.assertTrue(inativa.ativo)

    def test_create_categoria_nome_vazio(self):
        response = self.client.post("/catalog/categorias/", json={"nome": "   "})
        self.assertEqual(response.status_code, 400)

    def test_create_categoria_mesmo_slug_retorna_existente(self):
        # "Áudio" e "Audio" normalizam para o mesmo slug: não duplica.
        existente = Categoria.objects.create(
            empresa=self.user.empresa, nome="Audio", slug="audio"
        )
        response = self.client.post("/catalog/categorias/", json={"nome": "Áudio"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], existente.id)
        self.assertEqual(Categoria.objects.count(), 1)


class SubcategoriaAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.categoria = Categoria.objects.create(
            empresa=self.user.empresa, nome="Acessórios", slug="acessorios"
        )

    def test_create_subcategoria(self):
        response = self.client.post(
            "/catalog/subcategorias/",
            json={"nome": "Caixa de Som", "categoria_id": self.categoria.id},
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nome"], "Caixa de Som")
        self.assertEqual(data["slug"], "caixa-de-som")
        self.assertEqual(data["categoria_id"], self.categoria.id)
        self.assertEqual(data["categoria_nome"], "Acessórios")

    def test_create_subcategoria_existente_retorna_a_mesma(self):
        existente = Subcategoria.objects.create(
            empresa=self.user.empresa,
            categoria=self.categoria,
            nome="Caixa de Som",
            slug="caixa-de-som",
        )
        response = self.client.post(
            "/catalog/subcategorias/",
            json={"nome": "caixa de som", "categoria_id": self.categoria.id},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["id"], existente.id)
        self.assertEqual(Subcategoria.objects.count(), 1)

    def test_create_subcategoria_categoria_de_outra_empresa(self):
        outro_client, outro_user = create_authenticated_client(
            username="outro", cnpj="60701190000104"
        )
        response = outro_client.post(
            "/catalog/subcategorias/",
            json={"nome": "Caixa de Som", "categoria_id": self.categoria.id},
        )
        self.assertEqual(response.status_code, 400)

    def test_create_subcategoria_nome_vazio(self):
        response = self.client.post(
            "/catalog/subcategorias/",
            json={"nome": "", "categoria_id": self.categoria.id},
        )
        self.assertEqual(response.status_code, 400)
