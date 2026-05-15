from decimal import Decimal
from pathlib import Path
from tempfile import NamedTemporaryFile

import pandas as pd
from django.test import TestCase
from rich.console import Console

from catalog.models import Produto, Variacao
from importer.services.importer import ImportadorPlanilha


def criar_planilha_teste(linhas: list[dict]) -> Path:
    colunas = [
        "[SKU - NUVEMSHOP] - [ID GESTAOCLICK]", "CODIGO DE BARRAS",
        "DESCRICAO_PRODUTO_GESTAOCLICK", "DESCRICAO_PRODUTO_SITE",
        "VARIACOES_PRODUTO", "CUSTO_PRODUTO", "PRECO_PRODUTO_LOJA",
        "PRECO_PRODUTO_SITE", "MARGEM_PRODUTO_SITE",
        "STATUS_NUVEMSHOP", "INTEGRACAO_GESTAOCAOCLICK_NUVEMSHOP",
    ]
    df = pd.DataFrame(linhas, columns=colunas)
    tmp = NamedTemporaryFile(suffix=".xlsx", delete=False)
    df.to_excel(tmp.name, sheet_name="lista_produtos_varejo", index=False)
    return Path(tmp.name)


class ImportadorTestCase(TestCase):
    def setUp(self):
        self.console = Console(quiet=True)

    def _linha(self, **overrides):
        base = {
            "[SKU - NUVEMSHOP] - [ID GESTAOCLICK]": "20099680632090001",
            "CODIGO DE BARRAS": "",
            "DESCRICAO_PRODUTO_GESTAOCLICK": "CABO APPLE",
            "DESCRICAO_PRODUTO_SITE": "CABO CARREGADOR APPLE USB-C",
            "VARIACOES_PRODUTO": "USB-C",
            "CUSTO_PRODUTO": "56.65",
            "PRECO_PRODUTO_LOJA": "239.00",
            "PRECO_PRODUTO_SITE": "169.90",
            "MARGEM_PRODUTO_SITE": "",
            "STATUS_NUVEMSHOP": "ATIVO",
            "INTEGRACAO_GESTAOCAOCLICK_NUVEMSHOP": "ATIVO",
        }
        base.update(overrides)
        return base

    def test_importar_linha_valida(self):
        caminho = criar_planilha_teste([self._linha()])
        rel = ImportadorPlanilha(caminho, self.console).executar()
        self.assertEqual(rel.produtos_criados, 1)
        self.assertEqual(rel.variacoes_criadas, 1)
        v = Variacao.objects.get(sku_nuvemshop="20099680632090001")
        self.assertEqual(v.custo, Decimal("56.65"))

    def test_pular_linha_sem_custo(self):
        caminho = criar_planilha_teste([self._linha(CUSTO_PRODUTO="______")])
        rel = ImportadorPlanilha(caminho, self.console).executar()
        self.assertEqual(rel.linhas_puladas, 1)
        self.assertEqual(Variacao.objects.count(), 0)

    def test_dry_run_nao_persiste(self):
        caminho = criar_planilha_teste([self._linha()])
        rel = ImportadorPlanilha(caminho, self.console, dry_run=True).executar()
        self.assertEqual(rel.variacoes_criadas, 1)
        self.assertEqual(Variacao.objects.count(), 0)

    def test_atualizar_sku_existente(self):
        produto = Produto.objects.create(
            nome_gestaoclick="ANTIGO", nome_site="ANTIGO SITE",
        )
        Variacao.objects.create(
            produto=produto, sku_nuvemshop="SKU-EXISTE",
            custo=Decimal("1.00"), preco_loja=Decimal("2.00"),
        )
        caminho = criar_planilha_teste([self._linha(**{
            "[SKU - NUVEMSHOP] - [ID GESTAOCLICK]": "SKU-EXISTE",
            "CUSTO_PRODUTO": "99.99",
            "PRECO_PRODUTO_SITE": "149.99",
        })])
        rel = ImportadorPlanilha(caminho, self.console).executar()
        self.assertEqual(rel.variacoes_atualizadas, 1)
        v = Variacao.objects.get(sku_nuvemshop="SKU-EXISTE")
        self.assertEqual(v.custo, Decimal("99.99"))
        self.assertEqual(v.preco_site, Decimal("149.99"))
