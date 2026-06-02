from ninja import NinjaAPI

from .auth import auth
from .auth_router import router as auth_router
from catalog.routers import (
    marca_router,
    categoria_router,
    subcategoria_router,
    produto_router,
    variacao_router,
)
from finance.routers import (
    categoria_router as finance_categoria_router,
    lancamento_router as finance_lancamento_router,
    dashboard_router as finance_dashboard_router,
)
from reports.routers import catalog_report_router, finance_report_router

api = NinjaAPI(
    title="Controle Interno Site Ibeize API",
    version="1.0.0",
    description="API interna para gerenciamento de catálogo e finanças.",
)


@api.get("/health", tags=["meta"])
def health(request):
    """Verifica se a API está respondendo."""
    return {"status": "ok"}


api.add_router("/auth", auth_router)

api.add_router("/catalog/marcas", marca_router, auth=auth)
api.add_router("/catalog/categorias", categoria_router, auth=auth)
api.add_router("/catalog/subcategorias", subcategoria_router, auth=auth)
api.add_router("/catalog/produtos", produto_router, auth=auth)
api.add_router("/catalog/variacoes", variacao_router, auth=auth)

api.add_router("/finance/categorias", finance_categoria_router, auth=auth)
api.add_router("/finance/lancamentos", finance_lancamento_router, auth=auth)
api.add_router("/finance/dashboard", finance_dashboard_router, auth=auth)

api.add_router("/reports/catalog", catalog_report_router, auth=auth)
api.add_router("/reports/finance", finance_report_router, auth=auth)
