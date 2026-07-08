from decimal import Decimal

from django.test import TestCase

from catalog.models import Categoria, Subcategoria, Produto
from config.testing import create_authenticated_client


class ProdutoAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.categoria = Categoria.objects.create(empresa=self.user.empresa, nome="Fones", slug="fones")
        self.subcategoria = Subcategoria.objects.create(empresa=self.user.empresa,
            nome="TWS", slug="tws", categoria=self.categoria,
        )

    def test_list_vazio(self):
        response = self.client.get("/catalog/produtos/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_create_produto(self):
        payload = {
            "nome_gestaoclick": "FONE GET",
            "nome_site": "FONE DE OUVIDO GET",
            "categoria_id": self.categoria.id,
            "subcategoria_id": self.subcategoria.id,
        }
        response = self.client.post("/catalog/produtos/", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["nome_site"], "FONE DE OUVIDO GET")
        self.assertEqual(data["categoria_nome"], "Fones")
        self.assertEqual(data["subcategoria_nome"], "TWS")

    def test_create_produto_rejeita_subcategoria_de_outra_categoria(self):
        outra_categoria = Categoria.objects.create(
            empresa=self.user.empresa, nome="Cabos", slug="cabos"
        )
        payload = {
            "nome_gestaoclick": "FONE GET",
            "nome_site": "FONE DE OUVIDO GET",
            "categoria_id": outra_categoria.id,
            "subcategoria_id": self.subcategoria.id,
        }
        response = self.client.post("/catalog/produtos/", json=payload)
        self.assertEqual(response.status_code, 400)

    def test_get_produto(self):
        produto = Produto.objects.create(empresa=self.user.empresa,
            nome_gestaoclick="X", nome_site="Y", categoria=self.categoria,
        )
        response = self.client.get(f"/catalog/produtos/{produto.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nome_site"], "Y")

    def test_patch_produto(self):
        produto = Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="X", nome_site="Y")
        response = self.client.patch(
            f"/catalog/produtos/{produto.id}",
            json={"nome_site": "Z"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["nome_site"], "Z")

    def test_archive_produto(self):
        produto = Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="X", nome_site="Y")
        response = self.client.post(f"/catalog/produtos/{produto.id}/archive")
        self.assertEqual(response.status_code, 200)
        produto.refresh_from_db()
        self.assertFalse(produto.ativo)

    def test_list_nao_inclui_inativos_por_padrao(self):
        Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="A", nome_site="ATIVO")
        inativo = Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="I", nome_site="INATIVO")
        inativo.ativo = False
        inativo.save()

        response = self.client.get("/catalog/produtos/")
        nomes = [p["nome_site"] for p in response.json()]
        self.assertIn("ATIVO", nomes)
        self.assertNotIn("INATIVO", nomes)

    def test_list_inclui_inativos_com_flag(self):
        Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="A", nome_site="ATIVO")
        inativo = Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="I", nome_site="INATIVO")
        inativo.ativo = False
        inativo.save()

        response = self.client.get("/catalog/produtos/?inativos=true")
        nomes = [p["nome_site"] for p in response.json()]
        self.assertEqual(len(nomes), 2)

    def test_busca_por_nome(self):
        Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="X", nome_site="FONE BLUETOOTH")
        Produto.objects.create(empresa=self.user.empresa, nome_gestaoclick="X", nome_site="CABO USB-C")
        response = self.client.get("/catalog/produtos/?q=fone")
        nomes = [p["nome_site"] for p in response.json()]
        self.assertEqual(nomes, ["FONE BLUETOOTH"])
