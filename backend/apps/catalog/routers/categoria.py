from typing import List

from ninja import Router

from accounts.tenancy import empresa_do_usuario
from catalog.models import Categoria
from catalog.schemas import CategoriaOut

router = Router(tags=["categorias"])


@router.get("/", response=List[CategoriaOut])
def list_categorias(request, inativos: bool = False):
    qs = Categoria.objects.filter(empresa=empresa_do_usuario(request))
    if not inativos:
        qs = qs.filter(ativo=True)
    return qs.order_by("nome")
