from ninja import Schema


class SubcategoriaIn(Schema):
    nome: str
    categoria_id: int


class SubcategoriaOut(Schema):
    id: int
    nome: str
    slug: str
    categoria_id: int
    categoria_nome: str
    ativo: bool

    @staticmethod
    def resolve_categoria_nome(obj) -> str:
        return obj.categoria.nome
