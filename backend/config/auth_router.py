from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.core.validators import validate_email
from django.db import transaction
from django.db.models import Q
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
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


class EmpresaUpdateIn(Schema):
    nome: str
    cnpj: str
    username: str
    email: str

    @field_validator("nome")
    @classmethod
    def nome_obrigatorio(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 2:
            raise ValueError("Informe o nome da empresa.")
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


class SenhaIn(Schema):
    senha_atual: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A nova senha deve ter pelo menos 8 caracteres.")
        return value


class EsqueciSenhaIn(Schema):
    email: str

    @field_validator("email")
    @classmethod
    def email_valido(cls, value: str) -> str:
        value = value.strip().lower()
        try:
            validate_email(value)
        except ValidationError as exc:
            raise ValueError("E-mail inválido.") from exc
        return value


class RedefinirSenhaIn(Schema):
    uid: str
    token: str
    nova_senha: str

    @field_validator("nova_senha")
    @classmethod
    def senha_minima(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("A nova senha deve ter pelo menos 8 caracteres.")
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


@router.put("/empresa", auth=auth, response=UserOut)
def atualizar_empresa(request, payload: EmpresaUpdateIn):
    """Atualiza os dados da empresa e as credenciais de acesso do usuário."""
    user = request.auth
    empresa = Empresa.objects.filter(user=user).first()
    if empresa is None:
        raise HttpError(403, "Usuário sem empresa vinculada.")

    cnpj = limpar_cnpj(payload.cnpj)
    if not cnpj_valido(cnpj):
        raise HttpError(400, "CNPJ inválido.")
    if Empresa.objects.filter(cnpj=cnpj).exclude(pk=empresa.pk).exists():
        raise HttpError(409, "Já existe uma empresa cadastrada com este CNPJ.")

    # Manter o username atual é permitido (contas legadas usam o e-mail);
    # um username novo precisa seguir o formato.
    username = normalizar_username(payload.username)
    if username != user.username and not username_valido(username):
        raise HttpError(400, USERNAME_MENSAGEM)

    outros = get_user_model().objects.exclude(pk=user.pk)
    if outros.filter(username__iexact=username).exists():
        raise HttpError(409, "Já existe uma conta com este usuário.")
    if outros.filter(
        Q(email__iexact=payload.email) | Q(username__iexact=payload.email)
    ).exists():
        raise HttpError(409, "Já existe uma conta com este e-mail.")

    with transaction.atomic():
        user.username = username
        user.email = payload.email
        user.first_name = payload.nome
        user.save(update_fields=["username", "email", "first_name"])
        empresa.nome = payload.nome
        empresa.cnpj = cnpj
        empresa.save(update_fields=["nome", "cnpj", "atualizado_em"])

    return user


@router.post("/alterar-senha", auth=auth, response=LogoutOut)
def alterar_senha(request, payload: SenhaIn):
    user = request.auth
    if not user.check_password(payload.senha_atual):
        raise HttpError(400, "Senha atual incorreta.")
    user.set_password(payload.nova_senha)
    user.save(update_fields=["password"])
    return LogoutOut(ok=True)


@router.post("/esqueci-senha", response=LogoutOut)
def esqueci_senha(request, payload: EsqueciSenhaIn):
    """
    Envia o link de redefinição de senha por e-mail. Responde sempre ok
    para não revelar quais e-mails estão cadastrados.
    """
    user = (
        get_user_model()
        .objects.filter(email__iexact=payload.email, is_active=True)
        .first()
    )
    if user is not None:
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        link = f"{settings.FRONTEND_URL}/redefinir-senha?uid={uid}&token={token}"
        send_mail(
            subject="Redefinição de senha — Controle Interno",
            message=(
                f"Olá,\n\n"
                f"Recebemos um pedido para redefinir a senha da sua conta "
                f"({user.username}).\n\n"
                f"Para criar uma nova senha, acesse o link abaixo:\n\n"
                f"{link}\n\n"
                f"Se você não fez este pedido, ignore este e-mail — "
                f"sua senha continua a mesma."
            ),
            from_email=None,
            recipient_list=[user.email],
        )
    return LogoutOut(ok=True)


@router.post("/redefinir-senha", response=LogoutOut)
def redefinir_senha(request, payload: RedefinirSenhaIn):
    """Valida o token do link enviado por e-mail e define a nova senha."""
    erro = HttpError(
        400, "Link de redefinição inválido ou expirado. Solicite um novo."
    )
    try:
        user_pk = force_str(urlsafe_base64_decode(payload.uid))
        user = get_user_model().objects.get(pk=user_pk, is_active=True)
    except (ValueError, OverflowError, get_user_model().DoesNotExist):
        raise erro

    if not default_token_generator.check_token(user, payload.token):
        raise erro

    user.set_password(payload.nova_senha)
    user.save(update_fields=["password"])
    return LogoutOut(ok=True)


@router.post("/logout", auth=auth, response=LogoutOut)
def logout(request):
    return LogoutOut(ok=True)
