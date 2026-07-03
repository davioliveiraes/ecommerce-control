from datetime import date
from typing import Optional

from django.http import HttpResponse
from ninja import Router

from accounts.tenancy import empresa_do_usuario
from reports.services.overview_report import gerar_relatorio_visao_geral

router = Router(tags=["reports:visao-geral"])


@router.get("/pdf")
def relatorio_visao_geral_pdf(
    request,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
):
    pdf_bytes = gerar_relatorio_visao_geral(
        empresa=empresa_do_usuario(request),
        data_inicio=data_inicio,
        data_fim=data_fim,
    )
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ecommerce-visao-geral.pdf"'
    return response
