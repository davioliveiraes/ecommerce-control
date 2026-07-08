from typing import List, Optional

from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError

from accounts.models import Empresa
from accounts.tenancy import empresa_do_usuario
from catalog.models import Categoria, Produto, Subcategoria, Variacao
from catalog.schemas import (
    ProdutoIn,
    ProdutoOut,
    ProdutoPatch,
    ProdutoComVariacoesIn,
    ProdutoComVariacoesOut,
)

router = Router(tags=["produtos"])


def _validar_referencias(
    empresa: Empresa,
    categoria_id: Optional[int],
    subcategoria_id: Optional[int],
) -> None:
    """Garante que categoria/subcategoria referenciadas pertencem à empresa
    e que a subcategoria, quando informada, pertence à categoria escolhida."""
    if categoria_id is not None and not Categoria.objects.filter(
        id=categoria_id, empresa=empresa
    ).exists():
        raise HttpError(400, "Categoria não encontrada para esta empresa.")
    if subcategoria_id is not None:
        subcategoria = Subcategoria.objects.filter(
            id=subcategoria_id, empresa=empresa
        ).first()
        if subcategoria is None:
            raise HttpError(400, "Subcategoria não encontrada para esta empresa.")
        if categoria_id is not None and subcategoria.categoria_id != categoria_id:
            raise HttpError(
                400, "Subcategoria não pertence à categoria selecionada."
            )


@router.get("/", response=List[ProdutoOut])
def list_produtos(request, inativos: bool = False, q: str = ""):
    """
    Lista produtos da empresa. Sem paginação (AG Grid pagina no client).
    Filtros opcionais:
    - ?inativos=true: inclui inativos
    - ?q=texto: busca em descricao_produto_site e descricao_produto_gestaoclick
    """
    qs = Produto.objects.select_related("categoria", "subcategoria").filter(
        empresa=empresa_do_usuario(request)
    )
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


@router.post(
    "/com-variacoes",
    response={201: ProdutoComVariacoesOut, 400: dict},
)
def create_produto_com_variacoes(request, payload: ProdutoComVariacoesIn):
    """
    Cria um novo produto + suas variações em uma única transação atômica.

    Todas as variações do payload são criadas (qualquer `id` informado é
    ignorado, pois o produto ainda não existe).

    Registrado ANTES de `/{produto_id}` porque o conversor de path do Ninja
    casa qualquer segmento; sem isso, `com-variacoes` cairia na rota dinâmica.

    Validações:
    - Pelo menos uma variação é obrigatória.
    - SKU duplicado entre as variações do payload: 400.
    """
    empresa = empresa_do_usuario(request)
    if not payload.variacoes:
        return 400, {"detail": "Pelo menos uma variação é obrigatória."}

    skus_no_payload = [v.sku_nuvemshop for v in payload.variacoes if v.sku_nuvemshop]
    if len(skus_no_payload) != len(set(skus_no_payload)):
        return 400, {"detail": "SKU duplicado no payload."}

    _validar_referencias(empresa, payload.categoria_id, payload.subcategoria_id)

    with transaction.atomic():
        produto = Produto.objects.create(
            empresa=empresa,
            nome_gestaoclick=payload.nome_gestaoclick,
            nome_site=payload.nome_site,
            descricao_produto_gestaoclick=payload.descricao_produto_gestaoclick,
            descricao_produto_site=payload.descricao_produto_site,
            categoria_id=payload.categoria_id,
            subcategoria_id=payload.subcategoria_id,
        )

        for v_payload in payload.variacoes:
            Variacao.objects.create(
                produto=produto,
                sku_nuvemshop=v_payload.sku_nuvemshop,
                id_gestaoclick=v_payload.id_gestaoclick,
                codigo_barras=v_payload.codigo_barras,
                descricao=v_payload.descricao,
                custo=v_payload.custo,
                preco_loja=v_payload.preco_loja,
                preco_site=v_payload.preco_site,
                preco_promocional=v_payload.preco_promocional,
                status_nuvemshop=v_payload.status_nuvemshop,
                status_integracao=v_payload.status_integracao,
                ativo=v_payload.ativo,
            )

    produto_serializado = (
        Produto.objects.select_related("categoria", "subcategoria").get(id=produto.id)
    )
    variacoes = produto.variacoes.select_related("produto").order_by("id")

    return 201, {
        "produto": produto_serializado,
        "variacoes": list(variacoes),
    }


@router.get("/{produto_id}", response=ProdutoOut)
def get_produto(request, produto_id: int):
    return get_object_or_404(
        Produto.objects.select_related("categoria", "subcategoria"),
        id=produto_id,
        empresa=empresa_do_usuario(request),
    )


@router.post("/", response={201: ProdutoOut})
def create_produto(request, payload: ProdutoIn):
    empresa = empresa_do_usuario(request)
    data = payload.dict()
    _validar_referencias(empresa, data.get("categoria_id"), data.get("subcategoria_id"))
    produto = Produto.objects.create(empresa=empresa, **data)
    return 201, produto


@router.put("/{produto_id}", response=ProdutoOut)
def update_produto(request, produto_id: int, payload: ProdutoIn):
    empresa = empresa_do_usuario(request)
    produto = get_object_or_404(Produto, id=produto_id, empresa=empresa)
    data = payload.dict()
    _validar_referencias(empresa, data.get("categoria_id"), data.get("subcategoria_id"))
    for field, value in data.items():
        setattr(produto, field, value)
    produto.save()
    return produto


@router.patch("/{produto_id}", response=ProdutoOut)
def patch_produto(request, produto_id: int, payload: ProdutoPatch):
    empresa = empresa_do_usuario(request)
    produto = get_object_or_404(Produto, id=produto_id, empresa=empresa)
    data = payload.dict(exclude_unset=True)
    _validar_referencias(empresa, data.get("categoria_id"), data.get("subcategoria_id"))
    for field, value in data.items():
        setattr(produto, field, value)
    produto.save()
    return produto


@router.post("/{produto_id}/archive", response=ProdutoOut)
def archive_produto(request, produto_id: int):
    """Soft delete: marca como inativo."""
    produto = get_object_or_404(
        Produto, id=produto_id, empresa=empresa_do_usuario(request)
    )
    produto.ativo = False
    produto.save(update_fields=["ativo"])
    return produto


@router.post("/{produto_id}/restore", response=ProdutoOut)
def restore_produto(request, produto_id: int):
    """Reativa produto arquivado."""
    produto = get_object_or_404(
        Produto, id=produto_id, empresa=empresa_do_usuario(request)
    )
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
    empresa = empresa_do_usuario(request)
    produto = get_object_or_404(Produto, id=produto_id, empresa=empresa)

    skus_no_payload = [v.sku_nuvemshop for v in payload.variacoes if v.sku_nuvemshop]
    if len(skus_no_payload) != len(set(skus_no_payload)):
        return 400, {"detail": "SKU duplicado no payload."}

    _validar_referencias(empresa, payload.categoria_id, payload.subcategoria_id)

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
        produto.categoria_id = payload.categoria_id
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
                "preco_promocional": v_payload.preco_promocional,
                "status_nuvemshop": v_payload.status_nuvemshop,
                "status_integracao": v_payload.status_integracao,
                "ativo": v_payload.ativo,
            }
            if v_payload.id is None:
                Variacao.objects.create(produto=produto, **campos)
            else:
                Variacao.objects.filter(id=v_payload.id).update(**campos)

    produto_serializado = (
        Produto.objects.select_related("categoria", "subcategoria").get(id=produto.id)
    )
    variacoes = produto.variacoes.select_related("produto").order_by("id")

    return 200, {
        "produto": produto_serializado,
        "variacoes": list(variacoes),
    }
