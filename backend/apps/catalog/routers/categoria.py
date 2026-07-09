from typing import List

from django.db.models import Q
from django.utils.text import slugify
from ninja import Router
from ninja.errors import HttpError

from accounts.tenancy import empresa_do_usuario
from catalog.models import Categoria
from catalog.schemas import CategoriaIn, CategoriaOut

router = Router(tags=["categorias"])


@router.get("/", response=List[CategoriaOut])
def list_categorias(request, inativos: bool = False):
    qs = Categoria.objects.filter(empresa=empresa_do_usuario(request))
    if not inativos:
        qs = qs.filter(ativo=True)
    return qs.order_by("nome")


@router.post("/", response={200: CategoriaOut, 201: CategoriaOut})
def create_categoria(request, payload: CategoriaIn):
    """
    Cria uma categoria para a empresa. Se já existir uma com o mesmo nome,
    retorna a existente (reativando-a se estiver inativa) em vez de duplicar.
    """
    empresa = empresa_do_usuario(request)
    nome = payload.nome.strip()
    if not nome:
        raise HttpError(400, "Informe o nome da categoria.")

    # O slug normaliza caixa e acentos ("Áudio" ≡ "audio") em qualquer banco.
    slug = slugify(nome) or "categoria"
    existente = Categoria.objects.filter(
        Q(nome__iexact=nome) | Q(slug=slug), empresa=empresa
    ).first()
    if existente is not None:
        if not existente.ativo:
            existente.ativo = True
            existente.save(update_fields=["ativo"])
        return 200, existente

    return 201, Categoria.objects.create(empresa=empresa, nome=nome, slug=slug)
