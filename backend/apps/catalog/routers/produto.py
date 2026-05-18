from typing import List

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router

from catalog.models import Produto
from catalog.schemas import ProdutoIn, ProdutoOut, ProdutoPatch

router = Router(tags=["produtos"])


@router.get("/", response=List[ProdutoOut])
def list_produtos(request, inativos: bool = False, q: str = ""):
    """
    Lista produtos. Sem paginação (AG Grid pagina no client).
    Filtros opcionais:
    - ?inativos=true: inclui inativos
    - ?q=texto: busca em nome_site e nome_gestaoclick
    """
    qs = Produto.objects.select_related("marca", "subcategoria")
    if not inativos:
        qs = qs.filter(ativo=True)
    if q:
        qs = qs.filter(Q(nome_site__icontains=q) | Q(nome_gestaoclick__icontains=q))
    return qs.order_by("nome_site")


@router.get("/{produto_id}", response=ProdutoOut)
def get_produto(request, produto_id: int):
    return get_object_or_404(
        Produto.objects.select_related("marca", "subcategoria"),
        id=produto_id,
    )


@router.post("/", response={201: ProdutoOut})
def create_produto(request, payload: ProdutoIn):
    produto = Produto.objects.create(**payload.dict())
    return 201, produto


@router.put("/{produto_id}", response=ProdutoOut)
def update_produto(request, produto_id: int, payload: ProdutoIn):
    produto = get_object_or_404(Produto, id=produto_id)
    for field, value in payload.dict().items():
        setattr(produto, field, value)
    produto.save()
    return produto


@router.patch("/{produto_id}", response=ProdutoOut)
def patch_produto(request, produto_id: int, payload: ProdutoPatch):
    produto = get_object_or_404(Produto, id=produto_id)
    data = payload.dict(exclude_unset=True)
    for field, value in data.items():
        setattr(produto, field, value)
    produto.save()
    return produto


@router.post("/{produto_id}/archive", response=ProdutoOut)
def archive_produto(request, produto_id: int):
    """Soft delete: marca como inativo."""
    produto = get_object_or_404(Produto, id=produto_id)
    produto.ativo = False
    produto.save(update_fields=["ativo"])
    return produto


@router.post("/{produto_id}/restore", response=ProdutoOut)
def restore_produto(request, produto_id: int):
    """Reativa produto arquivado."""
    produto = get_object_or_404(Produto, id=produto_id)
    produto.ativo = True
    produto.save(update_fields=["ativo"])
    return produto
