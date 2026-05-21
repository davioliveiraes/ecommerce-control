from datetime import date
from typing import List, Optional

from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router

from finance.models import LancamentoFinanceiro
from finance.schemas import (
    LancamentoFinanceiroIn,
    LancamentoFinanceiroOut,
    LancamentoFinanceiroPatch,
)

router = Router(tags=["finance:lancamentos"])


@router.get("/", response=List[LancamentoFinanceiroOut])
def list_lancamentos(
    request,
    inativos: bool = False,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    categoria_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    q: str = "",
):
    qs = LancamentoFinanceiro.objects.select_related("categoria")
    if not inativos:
        qs = qs.filter(ativo=True)
    if tipo:
        qs = qs.filter(tipo=tipo)
    if status:
        qs = qs.filter(status=status)
    if categoria_id is not None:
        qs = qs.filter(categoria_id=categoria_id)
    if data_inicio is not None:
        qs = qs.filter(data_lancamento__gte=data_inicio)
    if data_fim is not None:
        qs = qs.filter(data_lancamento__lte=data_fim)
    if q:
        qs = qs.filter(Q(descricao__icontains=q) | Q(observacoes__icontains=q))
    return qs.order_by("-data_lancamento", "-id")


@router.get("/{lancamento_id}", response=LancamentoFinanceiroOut)
def get_lancamento(request, lancamento_id: int):
    return get_object_or_404(
        LancamentoFinanceiro.objects.select_related("categoria"),
        id=lancamento_id,
    )


@router.post("/", response={201: LancamentoFinanceiroOut})
def create_lancamento(request, payload: LancamentoFinanceiroIn):
    lancamento = LancamentoFinanceiro.objects.create(**payload.dict())
    return 201, lancamento


@router.put("/{lancamento_id}", response=LancamentoFinanceiroOut)
def update_lancamento(
    request, lancamento_id: int, payload: LancamentoFinanceiroIn
):
    lancamento = get_object_or_404(LancamentoFinanceiro, id=lancamento_id)
    for field, value in payload.dict().items():
        setattr(lancamento, field, value)
    lancamento.save()
    return lancamento


@router.patch("/{lancamento_id}", response=LancamentoFinanceiroOut)
def patch_lancamento(
    request, lancamento_id: int, payload: LancamentoFinanceiroPatch
):
    lancamento = get_object_or_404(LancamentoFinanceiro, id=lancamento_id)
    for field, value in payload.dict(exclude_unset=True).items():
        setattr(lancamento, field, value)
    lancamento.save()
    return lancamento


@router.post("/{lancamento_id}/archive", response=LancamentoFinanceiroOut)
def archive_lancamento(request, lancamento_id: int):
    lancamento = get_object_or_404(LancamentoFinanceiro, id=lancamento_id)
    lancamento.ativo = False
    lancamento.save(update_fields=["ativo"])
    return lancamento


@router.post("/{lancamento_id}/marcar-pago", response=LancamentoFinanceiroOut)
def marcar_pago(request, lancamento_id: int):
    lancamento = get_object_or_404(LancamentoFinanceiro, id=lancamento_id)
    lancamento.status = "PAGO"
    lancamento.save(update_fields=["status"])
    return lancamento
