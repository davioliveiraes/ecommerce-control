from django.contrib.auth import get_user_model
from ninja.testing import TestClient

from accounts.models import Empresa
from config.api import api
from config.auth import create_auth_token


def create_authenticated_client(username="tester", cnpj="11222333000181"):
    """
    Cria usuário + empresa (tenant) e retorna um client autenticado.

    A empresa fica acessível via `user.empresa` para escopar os objetos
    criados diretamente pelo ORM nos testes.
    """
    user_model = get_user_model()
    user = user_model.objects.create_user(
        username=username,
        password="teste-12345",
        email=f"{username}@example.com",
    )
    Empresa.objects.create(user=user, nome=f"Empresa {username}", cnpj=cnpj)
    token = create_auth_token(user)
    return TestClient(api, headers={"Authorization": f"Bearer {token}"}), user
