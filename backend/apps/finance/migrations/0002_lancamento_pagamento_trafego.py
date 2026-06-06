from django.db import migrations, models


def criar_categorias_padrao(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("finance", "CategoriaFinanceira")
    categorias = [
        ("Vendas NuvemShop", "vendas-nuvemshop", "#0A0A0A"),
        ("Plano NuvemShop", "nuvemshop-plano", "#262626"),
        ("Hospedagem & Domínio", "hospedagem-dominio", "#404040"),
        ("E-mail Profissional", "email-profissional", "#525252"),
        ("Equipe Ecommerce", "equipe-ecommerce", "#737373"),
        ("Marketing & Tráfego", "marketing-trafego", "#8A8A8A"),
        ("Taxas de Meios de Pagamento", "taxas-meios-pagamento", "#A3A3A3"),
        ("Embalagens & Frete", "embalagens-frete", "#BFBFBF"),
    ]
    for nome, slug, cor_hex in categorias:
        CategoriaFinanceira.objects.get_or_create(
            slug=slug,
            defaults={"nome": nome, "cor_hex": cor_hex},
        )


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="lancamentofinanceiro",
            name="fonte_trafego",
            field=models.CharField(
                blank=True,
                default="",
                max_length=100,
                verbose_name="fonte de tráfego",
            ),
        ),
        migrations.AddField(
            model_name="lancamentofinanceiro",
            name="forma_pagamento",
            field=models.CharField(
                blank=True,
                choices=[
                    ("PIX", "Pix"),
                    ("CARTAO_CREDITO", "Cartão de crédito"),
                    ("BOLETO", "Boleto"),
                    ("NUVEMPAGO", "NuvemPago"),
                    ("OUTRO", "Outro"),
                ],
                default="",
                max_length=20,
                verbose_name="forma de pagamento",
            ),
        ),
        migrations.AddField(
            model_name="lancamentofinanceiro",
            name="meio_pagamento",
            field=models.CharField(
                blank=True,
                choices=[
                    ("NUVEMPAGO", "NuvemPago"),
                    ("MERCADO_PAGO", "Mercado Pago"),
                    ("PAGSEGURO", "PagSeguro"),
                    ("MANUAL", "Manual"),
                    ("OUTRO", "Outro"),
                ],
                default="",
                max_length=20,
                verbose_name="meio/provedor de pagamento",
            ),
        ),
        migrations.AddField(
            model_name="lancamentofinanceiro",
            name="quantidade_parcelas",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                verbose_name="quantidade de parcelas",
            ),
        ),
        migrations.AddField(
            model_name="lancamentofinanceiro",
            name="quantidade_vendas",
            field=models.PositiveIntegerField(
                default=1,
                help_text="Quantidade de vendas agregadas neste lançamento. Use 1 para lançamento individual.",
                verbose_name="quantidade de vendas",
            ),
        ),
        migrations.AddIndex(
            model_name="lancamentofinanceiro",
            index=models.Index(
                fields=["forma_pagamento", "data_lancamento"],
                name="finance_lan_forma_p_67a2b0_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="lancamentofinanceiro",
            index=models.Index(
                fields=["meio_pagamento", "data_lancamento"],
                name="finance_lan_meio_pa_f298cd_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="lancamentofinanceiro",
            index=models.Index(
                fields=["fonte_trafego", "data_lancamento"],
                name="finance_lan_fonte_t_21311b_idx",
            ),
        ),
        migrations.RunPython(criar_categorias_padrao, migrations.RunPython.noop),
    ]
