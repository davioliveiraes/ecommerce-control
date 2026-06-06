"""Popular o banco com lançamentos financeiros de demonstração.

Útil para mostrar o dashboard preenchido em ambiente de portfólio/demo.
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from finance.models import CategoriaFinanceira, LancamentoFinanceiro


class Command(BaseCommand):
    help = "Popula o banco com lançamentos financeiros de exemplo para demo."

    def add_arguments(self, parser):
        parser.add_argument(
            "--meses",
            type=int,
            default=6,
            help="Quantos meses para trás gerar dados (padrão: 6).",
        )
        parser.add_argument(
            "--limpar",
            action="store_true",
            help="Apaga todos os lançamentos antes de popular.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        meses = options["meses"]
        limpar = options["limpar"]

        if limpar:
            removidos, _ = LancamentoFinanceiro.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Removidos {removidos} lançamentos."))

        categorias = {c.slug: c for c in CategoriaFinanceira.objects.all()}
        slugs_necessarios = {
            "vendas-nuvemshop",
            "nuvemshop-plano",
            "hospedagem-dominio",
            "email-profissional",
            "equipe-ecommerce",
            "marketing-trafego",
            "taxas-meios-pagamento",
            "embalagens-frete",
        }
        faltantes = slugs_necessarios - set(categorias.keys())
        if faltantes:
            self.stdout.write(self.style.ERROR(
                f"Categorias ausentes no banco: {sorted(faltantes)}. "
                "Rode as migrations antes."
            ))
            return

        hoje = date.today()
        criados = 0
        random.seed(42)

        for offset in range(meses):
            mes_referencia = (hoje.replace(day=1) - timedelta(days=offset * 30)).replace(day=1)

            criados += self._gerar_vendas_do_mes(mes_referencia, categorias)
            criados += self._gerar_despesas_fixas_do_mes(mes_referencia, categorias)
            criados += self._gerar_custos_variaveis_do_mes(mes_referencia, categorias)

        self.stdout.write(self.style.SUCCESS(f"{criados} lançamentos criados."))

    def _gerar_vendas_do_mes(self, mes_referencia, categorias):
        cat = categorias["vendas-nuvemshop"]
        contagem = 0
        for _ in range(random.randint(8, 14)):
            dia = random.randint(1, 28)
            data = mes_referencia.replace(day=dia)
            valor = Decimal(str(round(random.uniform(80, 950), 2)))
            qtd_vendas = random.randint(1, 6)
            forma = random.choice(["PIX", "CARTAO_CREDITO", "BOLETO", "NUVEMPAGO"])
            meio = random.choice(["NUVEMPAGO", "MERCADO_PAGO", "PAGSEGURO"])
            parcelas = random.choice([None, 1, 2, 3, 6, 12]) if forma == "CARTAO_CREDITO" else 1
            fonte = random.choice(["organico", "meta-ads", "google-ads", "instagram", "direto"])

            LancamentoFinanceiro.objects.create(
                descricao=f"Vendas NuvemShop — {data.strftime('%d/%m/%Y')}",
                tipo="RECEITA",
                categoria=cat,
                valor=valor * qtd_vendas,
                data_lancamento=data,
                status="PAGO",
                forma_pagamento=forma,
                meio_pagamento=meio,
                quantidade_parcelas=parcelas,
                quantidade_vendas=qtd_vendas,
                fonte_trafego=fonte,
            )
            contagem += 1
        return contagem

    def _gerar_despesas_fixas_do_mes(self, mes_referencia, categorias):
        fixos = [
            ("nuvemshop-plano", "Plano NuvemShop — mensalidade", "199.00", 5, "BOLETO"),
            ("hospedagem-dominio", "Hospedagem & domínio do site", "89.90", 7, "PIX"),
            ("email-profissional", "E-mail profissional", "34.90", 7, "CARTAO_CREDITO"),
            ("equipe-ecommerce", "Equipe ecommerce — salário", "3200.00", 5, "PIX"),
        ]
        contagem = 0
        for slug, descricao, valor, dia, forma in fixos:
            data = mes_referencia.replace(day=dia)
            status = "PAGO" if data <= date.today() else "PENDENTE"
            LancamentoFinanceiro.objects.create(
                descricao=descricao,
                tipo="DESPESA",
                categoria=categorias[slug],
                valor=Decimal(valor),
                data_lancamento=data,
                status=status,
                forma_pagamento=forma,
                meio_pagamento="MANUAL",
            )
            contagem += 1
        return contagem

    def _gerar_custos_variaveis_do_mes(self, mes_referencia, categorias):
        contagem = 0

        valor_marketing = Decimal(str(round(random.uniform(450, 1800), 2)))
        LancamentoFinanceiro.objects.create(
            descricao="Marketing & tráfego pago",
            tipo="DESPESA",
            categoria=categorias["marketing-trafego"],
            valor=valor_marketing,
            data_lancamento=mes_referencia.replace(day=random.randint(1, 28)),
            status="PAGO",
            forma_pagamento="CARTAO_CREDITO",
            meio_pagamento="MANUAL",
        )
        contagem += 1

        valor_taxas = Decimal(str(round(random.uniform(120, 480), 2)))
        LancamentoFinanceiro.objects.create(
            descricao="Taxas de meios de pagamento",
            tipo="DESPESA",
            categoria=categorias["taxas-meios-pagamento"],
            valor=valor_taxas,
            data_lancamento=mes_referencia.replace(day=28),
            status="PAGO",
            forma_pagamento="OUTRO",
            meio_pagamento="NUVEMPAGO",
        )
        contagem += 1

        for _ in range(random.randint(3, 6)):
            valor = Decimal(str(round(random.uniform(8, 45), 2)))
            qtd = random.randint(1, 5)
            data = mes_referencia.replace(day=random.randint(1, 28))
            LancamentoFinanceiro.objects.create(
                descricao=f"Embalagens & frete — pedido {data.strftime('%d/%m')}",
                tipo="CUSTO",
                categoria=categorias["embalagens-frete"],
                valor=valor * qtd,
                data_lancamento=data,
                status="PAGO",
                forma_pagamento="PIX",
                meio_pagamento="MANUAL",
                quantidade_vendas=qtd,
            )
            contagem += 1

        return contagem
