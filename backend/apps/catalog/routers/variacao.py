from typing import List, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from accounts.tenancy import empresa_do_usuario
from catalog.models import Produto, Variacao
from catalog.schemas import VariacaoIn, VariacaoOut, VariacaoPatch

router = Router(tags=["variacoes"])


@router.get("/", response=List[VariacaoOut])
def list_variacoes(
    request,
    inativos: bool = False,
    produto_id: Optional[int] = None,
    q: str = "",
):
    """
    Lista variações da empresa. Sem paginação (AG Grid pagina no client).
    Filtros opcionais:
    - ?inativos=true: inclui inativas
    - ?produto_id=N: só variações desse produto
    - ?q=texto: busca em SKU, descrição, nome do produto
    """
    qs = Variacao.objects.select_related("produto").filter(
        produto__empresa=empresa_do_usuario(request)
    )
    if not inativos:
        qs = qs.filter(ativo=True)
    if produto_id is not None:
        qs = qs.filter(produto_id=produto_id)
    if q:
        qs = qs.filter(
            Q(sku_nuvemshop__icontains=q)
            | Q(descricao__icontains=q)
            | Q(produto__nome_site__icontains=q)
        )
    return qs.order_by("produto__nome_site", "descricao")


@router.get("/{variacao_id}", response=VariacaoOut)
def get_variacao(request, variacao_id: int):
    return get_object_or_404(
        Variacao.objects.select_related("produto"),
        id=variacao_id,
        produto__empresa=empresa_do_usuario(request),
    )


@router.post("/", response={201: VariacaoOut})
def create_variacao(request, payload: VariacaoIn):
    empresa = empresa_do_usuario(request)
    data = payload.dict()
    if not Produto.objects.filter(id=data.get("produto_id"), empresa=empresa).exists():
        raise HttpError(400, "Produto não encontrado para esta empresa.")
    variacao = Variacao.objects.create(**data)
    return 201, variacao


@router.put("/{variacao_id}", response=VariacaoOut)
def update_variacao(request, variacao_id: int, payload: VariacaoIn):
    empresa = empresa_do_usuario(request)
    variacao = get_object_or_404(
        Variacao, id=variacao_id, produto__empresa=empresa
    )
    data = payload.dict()
    if data.get("produto_id") != variacao.produto_id and not Produto.objects.filter(
        id=data.get("produto_id"), empresa=empresa
    ).exists():
        raise HttpError(400, "Produto não encontrado para esta empresa.")
    for field, value in data.items():
        setattr(variacao, field, value)
    variacao.save()
    return variacao


@router.patch("/{variacao_id}", response=VariacaoOut)
def patch_variacao(request, variacao_id: int, payload: VariacaoPatch):
    empresa = empresa_do_usuario(request)
    variacao = get_object_or_404(
        Variacao, id=variacao_id, produto__empresa=empresa
    )
    data = payload.dict(exclude_unset=True)
    if "produto_id" in data and data["produto_id"] != variacao.produto_id:
        if not Produto.objects.filter(id=data["produto_id"], empresa=empresa).exists():
            raise HttpError(400, "Produto não encontrado para esta empresa.")
    for field, value in data.items():
        setattr(variacao, field, value)
    variacao.save()
    return variacao


@router.post("/{variacao_id}/archive", response=VariacaoOut)
def archive_variacao(request, variacao_id: int):
    """Soft delete."""
    variacao = get_object_or_404(
        Variacao, id=variacao_id, produto__empresa=empresa_do_usuario(request)
    )
    variacao.ativo = False
    variacao.save(update_fields=["ativo"])
    return variacao


@router.post("/{variacao_id}/restore", response=VariacaoOut)
def restore_variacao(request, variacao_id: int):
    variacao = get_object_or_404(
        Variacao, id=variacao_id, produto__empresa=empresa_do_usuario(request)
    )
    variacao.ativo = True
    variacao.save(update_fields=["ativo"])
    return variacao
