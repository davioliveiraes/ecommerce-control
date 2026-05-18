from ninja import Schema


class MarcaOut(Schema):
    id: int
    nome: str
    slug: str
    ativo: bool
