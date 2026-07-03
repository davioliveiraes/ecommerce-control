from typing import List

from ninja import Router

from accounts.tenancy import empresa_do_usuario
from catalog.models import Marca
from catalog.schemas import MarcaOut

router = Router(tags=["marcas"])


@router.get("/", response=List[MarcaOut])
def list_marcas(request, inativos: bool = False):
    """Lista marcas da empresa. Por padrão só ativas; ?inativos=true inclui todas."""
    qs = Marca.objects.filter(empresa=empresa_do_usuario(request))
    if not inativos:
        qs = qs.filter(ativo=True)
    return qs.order_by("nome")
