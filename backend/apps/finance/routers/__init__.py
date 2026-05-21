from .categoria_financeira import router as categoria_router
from .lancamento_financeiro import router as lancamento_router
from .dashboard import router as dashboard_router

__all__ = ["categoria_router", "lancamento_router", "dashboard_router"]
