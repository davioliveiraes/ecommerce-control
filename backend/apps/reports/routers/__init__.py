from .catalog import router as catalog_report_router
from .finance import router as finance_report_router
from .visao_geral import router as visao_geral_report_router

__all__ = [
    "catalog_report_router",
    "finance_report_router",
    "visao_geral_report_router",
]
