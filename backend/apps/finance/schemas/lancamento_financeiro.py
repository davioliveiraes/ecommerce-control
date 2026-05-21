from datetime import date
from decimal import Decimal
from typing import Optional

from ninja import Schema


class LancamentoFinanceiroIn(Schema):
    descricao: str
    tipo: str  # CUSTO | RECEITA | DESPESA
    categoria_id: Optional[int] = None
    valor: Decimal
    data_lancamento: date
    status: str = "PENDENTE"
    observacoes: str = ""


class LancamentoFinanceiroOut(Schema):
    id: int
    descricao: str
    tipo: str
    categoria_id: Optional[int] = None
    categoria_nome: Optional[str] = None
    categoria_cor_hex: Optional[str] = None
    valor: Decimal
    data_lancamento: date
    status: str
    observacoes: str
    ativo: bool

    @staticmethod
    def resolve_categoria_nome(obj) -> Optional[str]:
        return obj.categoria.nome if obj.categoria else None

    @staticmethod
    def resolve_categoria_cor_hex(obj) -> Optional[str]:
        return obj.categoria.cor_hex if obj.categoria else None


class LancamentoFinanceiroPatch(Schema):
    descricao: Optional[str] = None
    tipo: Optional[str] = None
    categoria_id: Optional[int] = None
    valor: Optional[Decimal] = None
    data_lancamento: Optional[date] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None
    ativo: Optional[bool] = None
