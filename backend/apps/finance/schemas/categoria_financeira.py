from typing import Optional

from ninja import Schema


class CategoriaFinanceiraIn(Schema):
    nome: str
    cor_hex: str = ""


class CategoriaFinanceiraOut(Schema):
    id: int
    nome: str
    slug: str
    cor_hex: str
    ativo: bool


class CategoriaFinanceiraPatch(Schema):
    nome: Optional[str] = None
    cor_hex: Optional[str] = None
    ativo: Optional[bool] = None
