from datetime import datetime
from typing import Optional

from ninja import Schema


class ProdutoIn(Schema):
    """Payload para criar/editar produto."""
    nome_gestaoclick: str
    nome_site: str
    marca_id: Optional[int] = None
    subcategoria_id: Optional[int] = None


class ProdutoOut(Schema):
    """Resposta padrão de produto."""
    id: int
    nome_gestaoclick: str
    nome_site: str
    marca_id: Optional[int] = None
    marca_nome: Optional[str] = None
    subcategoria_id: Optional[int] = None
    subcategoria_nome: Optional[str] = None
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    @staticmethod
    def resolve_marca_nome(obj) -> Optional[str]:
        return obj.marca.nome if obj.marca else None

    @staticmethod
    def resolve_subcategoria_nome(obj) -> Optional[str]:
        return obj.subcategoria.nome if obj.subcategoria else None


class ProdutoPatch(Schema):
    """Atualização parcial."""
    nome_gestaoclick: Optional[str] = None
    nome_site: Optional[str] = None
    marca_id: Optional[int] = None
    subcategoria_id: Optional[int] = None
    ativo: Optional[bool] = None
