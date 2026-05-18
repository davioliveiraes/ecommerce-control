from typing import List

from ninja import Router

from catalog.models import Marca
from catalog.schemas import MarcaOut

router = Router(tags=["marcas"])


@router.get("/", response=List[MarcaOut])
def list_marcas(request, inativos: bool = False):
    """Lista marcas. Por padrão só ativas; ?inativos=true inclui todas."""
    qs = Marca.objects.all() if inativos else Marca.objects.filter(ativo=True)
    return qs.order_by("nome")
