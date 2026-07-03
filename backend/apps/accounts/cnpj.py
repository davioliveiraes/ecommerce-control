"""Validação de CNPJ (algoritmo oficial dos dígitos verificadores)."""

import re


def limpar_cnpj(valor: str) -> str:
    """Remove máscara, mantendo apenas os dígitos."""
    return re.sub(r"\D", "", valor or "")


def _digito_verificador(digitos: str, pesos: list[int]) -> int:
    soma = sum(int(d) * p for d, p in zip(digitos, pesos))
    resto = soma % 11
    return 0 if resto < 2 else 11 - resto


def cnpj_valido(valor: str) -> bool:
    cnpj = limpar_cnpj(valor)
    if len(cnpj) != 14 or len(set(cnpj)) == 1:
        return False
    pesos1 = [5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2]
    pesos2 = [6] + pesos1
    dv1 = _digito_verificador(cnpj[:12], pesos1)
    dv2 = _digito_verificador(cnpj[:12] + str(dv1), pesos2)
    return cnpj[12:] == f"{dv1}{dv2}"


def formatar_cnpj(valor: str) -> str:
    cnpj = limpar_cnpj(valor)
    if len(cnpj) != 14:
        return valor
    return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
