"""Validação do usuário de acesso (username escolhido pela empresa)."""

import re

# Sem "@" de propósito: o login aceita usuário ou e-mail no mesmo campo,
# então usernames não podem ocupar o espaço de e-mails.
USERNAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,29}$")

USERNAME_MENSAGEM = (
    "O usuário deve ter de 3 a 30 caracteres, começar com letra ou número e "
    "usar apenas letras minúsculas, números, ponto, hífen e underline."
)


def normalizar_username(value: str) -> str:
    return value.strip().lower()


def username_valido(value: str) -> bool:
    return bool(USERNAME_RE.match(value))
