from typing import List

from ninja import Router

from catalog.models import Categoria
from catalog.schemas import CategoriaOut

router = Router(tags=["categorias"])


@router.get("/", response=List[CategoriaOut])
def list_categorias(request, inativos: bool = False):
    qs = Categoria.objects.all() if inativos else Categoria.objects.filter(ativo=True)
    return qs.order_by("nome")
