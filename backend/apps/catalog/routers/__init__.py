from .categoria import router as categoria_router
from .subcategoria import router as subcategoria_router
from .produto import router as produto_router
from .variacao import router as variacao_router

__all__ = [
    "categoria_router",
    "subcategoria_router",
    "produto_router",
    "variacao_router",
]
