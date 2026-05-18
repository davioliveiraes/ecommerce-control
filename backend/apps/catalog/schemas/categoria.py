from ninja import Schema


class CategoriaOut(Schema):
    id: int
    nome: str
    slug: str
    ativo: bool
