from decimal import Decimal

from django.test import TestCase

from catalog.models import Produto, Variacao
from config.testing import create_authenticated_client


class ProdutoComVariacoesTestCase(TestCase):
    def setUp(self):
        self.client, self.user = create_authenticated_client()
        self.produto = Produto.objects.create(empresa=self.user.empresa, 
            descricao_produto_site="FONE TESTE",
            descricao_produto_gestaoclick="FONE TESTE GC",
        )
        self.v1 = Variacao.objects.create(
            produto=self.produto,
            sku_nuvemshop="SKU-1",
            descricao="USB-C",
            custo=Decimal("10.00"),
            preco_loja=Decimal("20.00"),
            preco_site=Decimal("25.00"),
        )
        self.v2 = Variacao.objects.create(
            produto=self.produto,
            sku_nuvemshop="SKU-2",
            descricao="Lightning",
            custo=Decimal("12.00"),
            preco_loja=Decimal("22.00"),
        )

    def _payload_base(self):
        return {
            "nome_gestaoclick": "",
            "nome_site": "",
            "descricao_produto_gestaoclick": "FONE TESTE GC",
            "descricao_produto_site": "FONE TESTE",
            "categoria_id": None,
            "subcategoria_id": None,
            "variacoes": [],
        }

    def test_atualiza_produto_e_variacoes_existentes(self):
        payload = self._payload_base()
        payload["descricao_produto_site"] = "FONE EDITADO"
        payload["variacoes"] = [
            {
                "id": self.v1.id,
                "sku_nuvemshop": "SKU-1-NOVO",
                "descricao": "USB-C",
                "custo": "15.00",
                "preco_loja": "30.00",
                "preco_site": "40.00",
                "preco_promocional": "35.00",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO",
                "ativo": True,
            },
        ]
        response = self.client.put(
            f"/catalog/produtos/{self.produto.id}/com-variacoes",
            json=payload,
        )
        self.assertEqual(response.status_code, 200)
        self.produto.refresh_from_db()
        self.v1.refresh_from_db()
        self.assertEqual(self.produto.descricao_produto_site, "FONE EDITADO")
        self.assertEqual(self.v1.sku_nuvemshop, "SKU-1-NOVO")
        self.assertEqual(self.v1.custo, Decimal("15.00"))
        self.assertEqual(self.v1.preco_promocional, Decimal("35.00"))

    def test_cria_nova_variacao(self):
        payload = self._payload_base()
        payload["variacoes"] = [
            {
                "sku_nuvemshop": "SKU-NOVO",
                "descricao": "USB-A",
                "custo": "8.00",
                "preco_loja": "18.00",
                "preco_site": None,
                "preco_promocional": "15.00",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO",
                "ativo": True,
            },
        ]
        response = self.client.put(
            f"/catalog/produtos/{self.produto.id}/com-variacoes",
            json=payload,
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            Variacao.objects.filter(
                produto=self.produto, sku_nuvemshop="SKU-NOVO"
            ).exists()
        )

    def test_rejeita_sku_duplicado_no_payload(self):
        payload = self._payload_base()
        payload["variacoes"] = [
            {
                "sku_nuvemshop": "DUP", "descricao": "A",
                "custo": "1", "preco_loja": "2",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO", "ativo": True,
            },
            {
                "sku_nuvemshop": "DUP", "descricao": "B",
                "custo": "1", "preco_loja": "2",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO", "ativo": True,
            },
        ]
        response = self.client.put(
            f"/catalog/produtos/{self.produto.id}/com-variacoes",
            json=payload,
        )
        self.assertEqual(response.status_code, 400)

    def test_rejeita_id_de_variacao_de_outro_produto(self):
        outro_produto = Produto.objects.create(empresa=self.user.empresa, descricao_produto_site="OUTRO")
        outra_variacao = Variacao.objects.create(
            produto=outro_produto, sku_nuvemshop="X",
            custo=Decimal("1"), preco_loja=Decimal("2"),
        )
        payload = self._payload_base()
        payload["variacoes"] = [
            {
                "id": outra_variacao.id,
                "sku_nuvemshop": "TENTATIVA",
                "descricao": "",
                "custo": "1", "preco_loja": "2",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO", "ativo": True,
            },
        ]
        response = self.client.put(
            f"/catalog/produtos/{self.produto.id}/com-variacoes",
            json=payload,
        )
        self.assertEqual(response.status_code, 400)

    def test_atomico_em_caso_de_erro(self):
        """Se algo falha na validação, nada é salvo."""
        descricao_original = self.produto.descricao_produto_site
        payload = self._payload_base()
        payload["descricao_produto_site"] = "DEVERIA REVERTER"
        payload["variacoes"] = [
            {
                "id": 999999,  # id que não existe
                "sku_nuvemshop": "X",
                "descricao": "",
                "custo": "1", "preco_loja": "2",
                "status_nuvemshop": "ATIVO",
                "status_integracao": "ATIVO", "ativo": True,
            },
        ]
        response = self.client.put(
            f"/catalog/produtos/{self.produto.id}/com-variacoes",
            json=payload,
        )
        self.assertEqual(response.status_code, 400)
        self.produto.refresh_from_db()
        self.assertEqual(self.produto.descricao_produto_site, descricao_original)
