from decimal import Decimal

from django.test import TestCase

from catalog.models import Produto, Variacao
from config.testing import create_authenticated_client


class VariacaoAPITestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.produto = Produto.objects.create(empresa=self.user.empresa, 
            nome_gestaoclick="FONE",
            nome_site="FONE DE OUVIDO",
            descricao_produto_gestaoclick="Fone com microfone embutido",
            descricao_produto_site="Fone de ouvido com microfone para escritório",
        )

    def test_create_variacao(self):
        payload = {
            "produto_id": self.produto.id,
            "sku_nuvemshop": "SKU001",
            "descricao": "USB-C",
            "custo": "10.00",
            "preco_loja": "20.00",
            "preco_site": "25.00",
            "preco_promocional": "18.00",
        }
        response = self.client.post("/catalog/variacoes/", json=payload)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["sku_nuvemshop"], "SKU001")
        self.assertEqual(data["produto_nome_site"], "FONE DE OUVIDO")
        self.assertEqual(data["produto_nome_gestaoclick"], "FONE")
        self.assertEqual(
            data["produto_descricao_site"],
            "Fone de ouvido com microfone para escritório",
        )
        self.assertEqual(
            data["produto_descricao_gestaoclick"],
            "Fone com microfone embutido",
        )
        # margem = (25 - 10) / 10 * 100 = 150%
        self.assertEqual(Decimal(data["margem_percentual"]), Decimal("150.00"))
        self.assertEqual(data["preco_promocional"], "18.00")
        self.assertEqual(
            Decimal(data["margem_promocional_percentual"]),
            Decimal("80.00"),
        )

    def test_margem_null_sem_preco_site(self):
        v = Variacao.objects.create(
            produto=self.produto, sku_nuvemshop="X",
            custo=Decimal("10.00"), preco_loja=Decimal("20.00"),
        )
        response = self.client.get(f"/catalog/variacoes/{v.id}")
        self.assertIsNone(response.json()["margem_percentual"])

    def test_patch_preco(self):
        v = Variacao.objects.create(
            produto=self.produto, sku_nuvemshop="X",
            custo=Decimal("10.00"), preco_loja=Decimal("20.00"),
        )
        response = self.client.patch(
            f"/catalog/variacoes/{v.id}",
            json={"preco_site": "30.00", "preco_promocional": "22.00"},
        )
        self.assertEqual(response.status_code, 200)
        v.refresh_from_db()
        self.assertEqual(v.preco_site, Decimal("30.00"))
        self.assertEqual(v.preco_promocional, Decimal("22.00"))

    def test_archive_variacao(self):
        v = Variacao.objects.create(
            produto=self.produto, sku_nuvemshop="X",
            custo=Decimal("1"), preco_loja=Decimal("2"),
        )
        response = self.client.post(f"/catalog/variacoes/{v.id}/archive")
        self.assertEqual(response.status_code, 200)
        v.refresh_from_db()
        self.assertFalse(v.ativo)

    def test_filtro_por_produto(self):
        outro_produto = Produto.objects.create(empresa=self.user.empresa, 
            nome_gestaoclick="OUTRO", nome_site="OUTRO SITE",
        )
        Variacao.objects.create(
            produto=self.produto, sku_nuvemshop="A",
            custo=Decimal("1"), preco_loja=Decimal("2"),
        )
        Variacao.objects.create(
            produto=outro_produto, sku_nuvemshop="B",
            custo=Decimal("1"), preco_loja=Decimal("2"),
        )
        response = self.client.get(f"/catalog/variacoes/?produto_id={self.produto.id}")
        skus = [v["sku_nuvemshop"] for v in response.json()]
        self.assertEqual(skus, ["A"])
