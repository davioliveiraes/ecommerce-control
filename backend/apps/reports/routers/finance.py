from datetime import date
from typing import List, Optional

from django.http import HttpResponse
from ninja import Query, Router

from reports.services.finance_report import gerar_relatorio_finance

router = Router(tags=["reports:finance"])


@router.get("/pdf")
def relatorio_finance_pdf(
    request,
    colunas: List[str] = Query(default=[]),
    incluir_inativos: bool = False,
    tipo: Optional[str] = None,
    status: Optional[str] = None,
    categoria_id: Optional[int] = None,
    data_inicio: Optional[date] = None,
    data_fim: Optional[date] = None,
    busca: str = "",
):
    pdf_bytes = gerar_relatorio_finance(
        colunas=colunas,
        incluir_inativos=incluir_inativos,
        tipo=tipo,
        status=status,
        categoria_id=categoria_id,
        data_inicio=data_inicio,
        data_fim=data_fim,
        busca=busca,
    )
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="ecommerce-finance.pdf"'
    return response
