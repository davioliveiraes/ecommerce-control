from typing import List

from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from ninja import Router

from finance.models import CategoriaFinanceira
from finance.schemas import (
    CategoriaFinanceiraIn,
    CategoriaFinanceiraOut,
    CategoriaFinanceiraPatch,
)

router = Router(tags=["finance:categorias"])


@router.get("/", response=List[CategoriaFinanceiraOut])
def list_categorias(request, inativos: bool = False):
    qs = (
        CategoriaFinanceira.objects.all()
        if inativos
        else CategoriaFinanceira.objects.filter(ativo=True)
    )
    return qs.order_by("nome")


@router.post("/", response={201: CategoriaFinanceiraOut})
def create_categoria(request, payload: CategoriaFinanceiraIn):
    categoria = CategoriaFinanceira.objects.create(
        nome=payload.nome,
        slug=slugify(payload.nome),
        cor_hex=payload.cor_hex,
    )
    return 201, categoria


@router.patch("/{categoria_id}", response=CategoriaFinanceiraOut)
def patch_categoria(
    request, categoria_id: int, payload: CategoriaFinanceiraPatch
):
    categoria = get_object_or_404(CategoriaFinanceira, id=categoria_id)
    data = payload.dict(exclude_unset=True)
    if "nome" in data:
        categoria.slug = slugify(data["nome"])
    for field, value in data.items():
        setattr(categoria, field, value)
    categoria.save()
    return categoria
