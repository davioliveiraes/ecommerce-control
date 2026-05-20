from typing import List

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router

from catalog.models import Produto, Variacao
from catalog.schemas import (
    ProdutoIn,
    ProdutoOut,
    ProdutoPatch,
    ProdutoComVariacoesIn,
    ProdutoComVariacoesOut,
)

router = Router(tags=["produtos"])


@router.get("/", response=List[ProdutoOut])
def list_produtos(request, inativos: bool = False, q: str = ""):
    """
    Lista produtos. Sem paginação (AG Grid pagina no client).
    Filtros opcionais:
    - ?inativos=true: inclui inativos
    - ?q=texto: busca em descricao_produto_site e descricao_produto_gestaoclick
    """
    qs = Produto.objects.select_related("marca", "subcategoria")
    if not inativos:
        qs = qs.filter(ativo=True)
    if q:
        qs = qs.filter(
            Q(descricao_produto_site__icontains=q)
            | Q(descricao_produto_gestaoclick__icontains=q)
            | Q(nome_site__icontains=q)
            | Q(nome_gestaoclick__icontains=q)
        )
    return qs.order_by("descricao_produto_site")


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


@router.put(
    "/{produto_id}/com-variacoes",
    response={200: ProdutoComVariacoesOut, 400: dict},
)
def update_produto_com_variacoes(
    request,
    produto_id: int,
    payload: ProdutoComVariacoesIn,
):
    """
    Atualiza produto + variações em uma única transação atômica.

    Comportamento das variações:
    - id presente e pertence ao produto: UPDATE
    - id ausente: CREATE (vinculada ao produto)
    - variações existentes não incluídas no payload: mantidas inalteradas
      (para arquivar, mande `ativo=False`; para soft-delete dedicado,
       use o endpoint `/variacoes/{id}/archive`).

    Validações:
    - SKU duplicado em variações do mesmo payload: 400
    - id de variação não pertencente ao produto: 400
    """
    produto = get_object_or_404(Produto, id=produto_id)

    skus_no_payload = [v.sku_nuvemshop for v in payload.variacoes if v.sku_nuvemshop]
    if len(skus_no_payload) != len(set(skus_no_payload)):
        return 400, {"detail": "SKU duplicado no payload."}

    ids_no_payload = {v.id for v in payload.variacoes if v.id is not None}
    if ids_no_payload:
        ids_no_banco = set(
            produto.variacoes.filter(id__in=ids_no_payload).values_list("id", flat=True)
        )
        ids_invalidos = ids_no_payload - ids_no_banco
        if ids_invalidos:
            return 400, {
                "detail": (
                    f"Variações {sorted(ids_invalidos)} não pertencem ao "
                    f"produto {produto_id}."
                )
            }

    with transaction.atomic():
        produto.nome_gestaoclick = payload.nome_gestaoclick
        produto.nome_site = payload.nome_site
        produto.descricao_produto_gestaoclick = payload.descricao_produto_gestaoclick
        produto.descricao_produto_site = payload.descricao_produto_site
        produto.marca_id = payload.marca_id
        produto.subcategoria_id = payload.subcategoria_id
        produto.save()

        for v_payload in payload.variacoes:
            campos = {
                "sku_nuvemshop": v_payload.sku_nuvemshop,
                "id_gestaoclick": v_payload.id_gestaoclick,
                "codigo_barras": v_payload.codigo_barras,
                "descricao": v_payload.descricao,
                "custo": v_payload.custo,
                "preco_loja": v_payload.preco_loja,
                "preco_site": v_payload.preco_site,
                "status_nuvemshop": v_payload.status_nuvemshop,
                "status_integracao": v_payload.status_integracao,
                "ativo": v_payload.ativo,
            }
            if v_payload.id is None:
                Variacao.objects.create(produto=produto, **campos)
            else:
                Variacao.objects.filter(id=v_payload.id).update(**campos)

    produto_serializado = (
        Produto.objects.select_related("marca", "subcategoria").get(id=produto.id)
    )
    variacoes = produto.variacoes.select_related("produto").order_by("id")

    return 200, {
        "produto": produto_serializado,
        "variacoes": list(variacoes),
    }
