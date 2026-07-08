from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from ninja import Schema

from .variacao import VariacaoOut


class ProdutoIn(Schema):
    """Payload para criar/editar produto."""
    nome_gestaoclick: str = ""
    nome_site: str = ""
    descricao_produto_gestaoclick: str = ""
    descricao_produto_site: str = ""
    categoria_id: Optional[int] = None
    subcategoria_id: Optional[int] = None


class ProdutoOut(Schema):
    """Resposta padrão de produto."""
    id: int
    nome_gestaoclick: str
    nome_site: str
    descricao_produto_gestaoclick: str
    descricao_produto_site: str
    categoria_id: Optional[int] = None
    categoria_nome: Optional[str] = None
    subcategoria_id: Optional[int] = None
    subcategoria_nome: Optional[str] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    @staticmethod
    def resolve_categoria_nome(obj) -> Optional[str]:
        return obj.categoria.nome if obj.categoria else None

    @staticmethod
    def resolve_subcategoria_nome(obj) -> Optional[str]:
        return obj.subcategoria.nome if obj.subcategoria else None


class ProdutoPatch(Schema):
    """Atualização parcial."""
    nome_gestaoclick: Optional[str] = None
    nome_site: Optional[str] = None
    descricao_produto_gestaoclick: Optional[str] = None
    descricao_produto_site: Optional[str] = None
    categoria_id: Optional[int] = None
    subcategoria_id: Optional[int] = None
    ativo: Optional[bool] = None


class VariacaoInComposto(Schema):
    """Variação dentro do payload composto.

    - `id` presente: atualiza variação existente.
    - `id` ausente: cria nova variação vinculada ao produto.
    """
    id: Optional[int] = None
    sku_nuvemshop: str = ""
    id_gestaoclick: str = ""
    codigo_barras: str = ""
    descricao: str = ""
    custo: Decimal
    preco_loja: Decimal
    preco_site: Optional[Decimal] = None
    preco_promocional: Optional[Decimal] = None
    status_nuvemshop: str = "ATIVO"
    status_integracao: str = "ATIVO"
    ativo: bool = True


class ProdutoComVariacoesIn(Schema):
    """Payload para salvar produto + suas variações em uma única transação."""
    nome_gestaoclick: str = ""
    nome_site: str = ""
    descricao_produto_gestaoclick: str = ""
    descricao_produto_site: str
    categoria_id: Optional[int] = None
    subcategoria_id: Optional[int] = None
    variacoes: List[VariacaoInComposto]


class ProdutoComVariacoesOut(Schema):
    """Resposta do salvamento composto: produto + todas as variações resultantes."""
    produto: ProdutoOut
    variacoes: List[VariacaoOut]
