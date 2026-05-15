"""Leitura da planilha Excel."""

from pathlib import Path
from typing import Iterator

import pandas as pd


COLUNAS_PLANILHA = {
    "[SKU - NUVEMSHOP] - [ID GESTAOCLICK]": "sku_nuvemshop",
    "CODIGO DE BARRAS": "codigo_barras",
    "DESCRICAO_PRODUTO_GESTAOCLICK": "nome_gestaoclick",
    "DESCRICAO_PRODUTO_SITE": "nome_site",
    "VARIACOES_PRODUTO": "descricao_variacao",
    "CUSTO_PRODUTO": "custo",
    "PRECO_PRODUTO_LOJA": "preco_loja",
    "PRECO_PRODUTO_SITE": "preco_site",
    "STATUS_NUVEMSHOP": "status_nuvemshop",
    "INTEGRACAO_GESTAOCAOCLICK_NUVEMSHOP": "status_integracao",
}

NOME_ABA = "lista_produtos_varejo"


def ler_planilha(caminho: Path) -> Iterator[dict]:
    df = pd.read_excel(
        caminho,
        sheet_name=NOME_ABA,
        dtype=str,
        keep_default_na=False,
    )
    faltantes = set(COLUNAS_PLANILHA.keys()) - set(df.columns)
    if faltantes:
        raise ValueError(
            f"Colunas faltantes na planilha: {faltantes}. "
            f"Encontradas: {list(df.columns)}"
        )

    for idx, row in df.iterrows():
        linha = {
            destino: row[origem]
            for origem, destino in COLUNAS_PLANILHA.items()
        }
        linha["linha_excel"] = idx + 2
        yield linha
