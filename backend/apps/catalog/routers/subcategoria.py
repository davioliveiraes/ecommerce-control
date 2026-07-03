from typing import List, Optional

from ninja import Router

from accounts.tenancy import empresa_do_usuario
from catalog.models import Subcategoria
from catalog.schemas import SubcategoriaOut

router = Router(tags=["subcategorias"])


@router.get("/", response=List[SubcategoriaOut])
def list_subcategorias(
    request,
    inativos: bool = False,
    categoria_id: Optional[int] = None,
):
    """
    Lista subcategorias da empresa. Filtros opcionais:
    - ?inativos=true: inclui inativas
    - ?categoria_id=N: só subcategorias dessa categoria
    """
    qs = Subcategoria.objects.select_related("categoria").filter(
        empresa=empresa_do_usuario(request)
    )
    if not inativos:
        qs = qs.filter(ativo=True)
    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)
    return qs.order_by("categoria__nome", "nome")
