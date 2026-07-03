from typing import List, Optional

from django.http import HttpResponse
from ninja import Query, Router

from accounts.tenancy import empresa_do_usuario
from reports.services.catalog_report import gerar_relatorio_catalogo

router = Router(tags=["reports:catalog"])


@router.get("/pdf")
def relatorio_catalogo_pdf(
    request,
    colunas: List[str] = Query(default=[]),
    incluir_inativos: bool = False,
    marca_id: Optional[int] = None,
    subcategoria_id: Optional[int] = None,
    busca: str = "",
    apenas_promocional: bool = False,
):
    pdf_bytes = gerar_relatorio_catalogo(
        empresa=empresa_do_usuario(request),
        colunas=colunas,
        incluir_inativos=incluir_inativos,
        marca_id=marca_id,
        subcategoria_id=subcategoria_id,
        busca=busca,
        apenas_promocional=apenas_promocional,
    )
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ecommerce-catalogo.pdf"'
    return response
