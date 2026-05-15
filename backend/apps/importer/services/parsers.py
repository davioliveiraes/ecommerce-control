"""Funções puras de parsing/normalização de valores da planilha."""

import math
from decimal import Decimal, InvalidOperation


EMPTY_VALUES = {"", "______", "_____", "____", "___", "__", "_", "nan", "none", "null"}


def is_empty(value) -> bool:
    if value is None:
        return True
    if isinstance(value, float) and math.isnan(value):
        return True
    return str(value).strip().lower() in EMPTY_VALUES


def parse_string(value) -> str:
    if is_empty(value):
        return ""
    return str(value).strip()


def parse_sku(value) -> str:
    """Converte SKU para string limpa, sem casas decimais nem notação científica."""
    if is_empty(value):
        return ""
    try:
        d = Decimal(str(value).strip())
        if d == d.to_integral_value():
            return str(int(d))
        return str(d)
    except (InvalidOperation, ValueError):
        return str(value).strip()


def parse_decimal(value) -> Decimal | None:
    """Converte valor monetário para Decimal. None se vazio. Levanta ValueError se inválido."""
    if is_empty(value):
        return None
    try:
        return Decimal(str(value)).quantize(Decimal("0.01"))
    except InvalidOperation as e:
        raise ValueError(f"Não foi possível converter '{value}' para Decimal") from e


def parse_status(value, default: str = "ATIVO") -> str:
    if is_empty(value):
        return default
    text = str(value).strip().upper()
    if text in ("ATIVO", "ATIVA", "A", "1", "TRUE", "SIM"):
        return "ATIVO"
    if text in ("INATIVO", "INATIVA", "I", "0", "FALSE", "NÃO", "NAO"):
        return "INATIVO"
    return default
