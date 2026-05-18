from ninja import NinjaAPI

from catalog.routers import (
    marca_router,
    categoria_router,
    subcategoria_router,
    produto_router,
    variacao_router,
)

api = NinjaAPI(
    title="Ibeize Ecommerce Control API",
    version="1.0.0",
    description="API interna para gerenciamento de catálogo e finanças.",
)


@api.get("/health", tags=["meta"])
def health(request):
    """Verifica se a API está respondendo."""
    return {"status": "ok"}


api.add_router("/catalog/marcas", marca_router)
api.add_router("/catalog/categorias", categoria_router)
api.add_router("/catalog/subcategorias", subcategoria_router)
api.add_router("/catalog/produtos", produto_router)
api.add_router("/catalog/variacoes", variacao_router)
