from typing import List

from django.shortcuts import get_object_or_404
from ninja import Router

from accounts.tenancy import empresa_do_usuario
from finance.models import VisaoGeralPeriodo
from finance.schemas import (
    VisaoGeralPeriodoIn,
    VisaoGeralPeriodoOut,
    VisaoGeralPeriodoPatch,
)

router = Router(tags=["finance:visao-geral"])


@router.get("/", response=List[VisaoGeralPeriodoOut])
def list_periodos(request, inativos: bool = False):
    """Lista os períodos da visão geral, do mais recente para o mais antigo."""
    qs = VisaoGeralPeriodo.objects.filter(empresa=empresa_do_usuario(request))
    if not inativos:
        qs = qs.filter(ativo=True)
    return qs.order_by("-data_inicio", "-id")


@router.get("/{periodo_id}", response=VisaoGeralPeriodoOut)
def get_periodo(request, periodo_id: int):
    return get_object_or_404(
        VisaoGeralPeriodo, id=periodo_id, empresa=empresa_do_usuario(request)
    )


@router.post("/", response={201: VisaoGeralPeriodoOut})
def create_periodo(request, payload: VisaoGeralPeriodoIn):
    periodo = VisaoGeralPeriodo.objects.create(
        empresa=empresa_do_usuario(request), **payload.dict()
    )
    return 201, periodo


@router.put("/{periodo_id}", response=VisaoGeralPeriodoOut)
def update_periodo(request, periodo_id: int, payload: VisaoGeralPeriodoIn):
    periodo = get_object_or_404(
        VisaoGeralPeriodo, id=periodo_id, empresa=empresa_do_usuario(request)
    )
    for field, value in payload.dict().items():
        setattr(periodo, field, value)
    periodo.save()
    return periodo


@router.patch("/{periodo_id}", response=VisaoGeralPeriodoOut)
def patch_periodo(request, periodo_id: int, payload: VisaoGeralPeriodoPatch):
    periodo = get_object_or_404(
        VisaoGeralPeriodo, id=periodo_id, empresa=empresa_do_usuario(request)
    )
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(periodo, field, value)
    periodo.save()
    return periodo


@router.delete("/{periodo_id}", response={204: None})
def delete_periodo(request, periodo_id: int):
    periodo = get_object_or_404(
        VisaoGeralPeriodo, id=periodo_id, empresa=empresa_do_usuario(request)
    )
    periodo.delete()  # soft delete (ativo=False)
    return 204, None
