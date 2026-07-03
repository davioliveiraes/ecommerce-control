from typing import Optional

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from ninja import Router, Schema
from ninja.errors import HttpError
from pydantic import field_validator

from accounts.cnpj import cnpj_valido, limpar_cnpj
from accounts.models import Empresa
from accounts.onboarding import semear_dados_iniciais
from accounts.username import (
    USERNAME_MENSAGEM,
    normalizar_username,
    username_valido,
)

from .auth import auth, authenticate_user, create_auth_token

router = Router(tags=["auth"])


class LoginIn(Schema):
    username: str
    password: str


class EmpresaOut(Schema):
    id: int
    nome: str
    cnpj: str


class UserOut(Schema):
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_staff: bool
    empresa: Optional[EmpresaOut] = None

    @staticmethod
    def resolve_empresa(obj):
        return Empresa.objects.filter(user=obj).first()


class LoginOut(Schema):
    token: str
    token_type: str = "Bearer"
    user: UserOut


class RegisterIn(Schema):
    nome: str
    cnpj: str
    username: str
    email: str
    password: str

    @field_validator("username")
    @classmethod
    def username_formato(cls, value: str) -> str:
        value = normalizar_username(value)
        if not username_valido(value):
            raise ValueError(USERNAME_MENSAGEM)
        return value

    @field_validator("email")
    @classmethod
    def email_valido(cls, value: str) -> str:
        value = value.strip().lower()
        try:
            validate_email(value)
        except ValidationError as exc:
            raise ValueError("E-mail inválido.") from exc
        return value

    @field_validator("nome")
    @classmethod
    def nome_obrigatorio(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Informe o nome da empresa.")
        return value

    @field_validator("password")
    @classmethod
    def senha_minima(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A senha deve ter pelo menos 8 caracteres.")
        return value


class LogoutOut(Schema):
    ok: bool


@router.post("/login", response=LoginOut)
def login(request, payload: LoginIn):
    user = authenticate_user(payload.username, payload.password)
    if user is None:
        raise HttpError(401, "Usuário ou senha inválidos.")

    return LoginOut(token=create_auth_token(user), user=user)


@router.post("/register", response={201: LoginOut})
def register(request, payload: RegisterIn):
    """
    Cadastro de empresa (lojista com CNPJ). Cria o usuário (login por usuário
    ou e-mail), a empresa e as categorias financeiras padrão; retorna token
    (auto-login).
    """
    cnpj = limpar_cnpj(payload.cnpj)
    if not cnpj_valido(cnpj):
        raise HttpError(400, "CNPJ inválido.")
    if Empresa.objects.filter(cnpj=cnpj).exists():
        raise HttpError(409, "Já existe uma empresa cadastrada com este CNPJ.")

    email = payload.email.lower()
    user_model = get_user_model()
    if user_model.objects.filter(username__iexact=payload.username).exists():
        raise HttpError(409, "Já existe uma conta com este usuário.")
    # username__iexact cobre contas legadas, criadas com username == e-mail.
    if user_model.objects.filter(
        Q(email__iexact=email) | Q(username__iexact=email)
    ).exists():
        raise HttpError(409, "Já existe uma conta com este e-mail.")

    with transaction.atomic():
        user = user_model.objects.create_user(
            username=payload.username,
            email=email,
            password=payload.password,
            first_name=payload.nome,
        )
        empresa = Empresa.objects.create(user=user, nome=payload.nome, cnpj=cnpj)
        semear_dados_iniciais(empresa)

    return 201, LoginOut(token=create_auth_token(user), user=user)


@router.get("/me", auth=auth, response=UserOut)
def me(request):
    return request.auth


@router.post("/logout", auth=auth, response=LogoutOut)
def logout(request):
    return LogoutOut(ok=True)
