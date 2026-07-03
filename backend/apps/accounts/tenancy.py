"""Helpers de multi-tenancy para os routers da API."""

from ninja.errors import HttpError

from .models import Empresa


def empresa_do_usuario(request) -> Empresa:
    """
    Resolve a empresa do usuário autenticado (request.auth).

    Todo endpoint de dados de negócio deve usar esta função e escopar
    querysets/criações pela empresa retornada.
    """
    empresa = Empresa.objects.filter(user=request.auth).first()
    if empresa is None:
        raise HttpError(403, "Usuário sem empresa vinculada.")
    return empresa
