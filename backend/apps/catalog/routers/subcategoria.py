from typing import List, Optional

from django.db.models import Q
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError

from accounts.tenancy import empresa_do_usuario
from catalog.models import Categoria, Subcategoria
from catalog.schemas import SubcategoriaIn, SubcategoriaOut

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


@router.post("/", response={200: SubcategoriaOut, 201: SubcategoriaOut})
def create_subcategoria(request, payload: SubcategoriaIn):
    """
    Cria uma subcategoria dentro de uma categoria da empresa. Se já existir
    uma com o mesmo nome na categoria, retorna a existente (reativando-a se
    estiver inativa) em vez de duplicar.
    """
    empresa = empresa_do_usuario(request)
    nome = payload.nome.strip()
    if not nome:
        raise HttpError(400, "Informe o nome da subcategoria.")

    categoria = Categoria.objects.filter(
        id=payload.categoria_id, empresa=empresa
    ).first()
    if categoria is None:
        raise HttpError(400, "Categoria não encontrada para esta empresa.")

    # O slug normaliza caixa e acentos ("Caixa de Som" ≡ "caixa-de-som").
    slug = slugify(nome) or "subcategoria"
    existente = Subcategoria.objects.filter(
        Q(nome__iexact=nome) | Q(slug=slug), categoria=categoria
    ).first()
    if existente is not None:
        if not existente.ativo:
            existente.ativo = True
            existente.save(update_fields=["ativo"])
        return 200, existente

    return 201, Subcategoria.objects.create(
        empresa=empresa, categoria=categoria, nome=nome, slug=slug
    )
