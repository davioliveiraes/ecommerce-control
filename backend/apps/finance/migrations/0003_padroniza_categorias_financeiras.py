from django.db import migrations


TARGET_CATEGORIES = {
    "godaddy-email-profissional": {
        "nome": "GoDaddy(Email Profissional)",
        "cor_hex": "#2563eb",
        "legacy_slugs": ["email-profissional"],
    },
    "godaddy-hospedagem": {
        "nome": "GoDaddy(Hospedagem)",
        "cor_hex": "#111827",
        "legacy_slugs": ["godaddy"],
    },
    "nuvemshop-nuvempago": {
        "nome": "NuvemShop(NuvemPago)",
        "cor_hex": "#1f4f8f",
        "legacy_slugs": ["nuvempago", "vendas-nuvempago"],
    },
    "nuvemshop-plano": {
        "nome": "NuvemShop(Plano)",
        "cor_hex": "#f97316",
        "legacy_slugs": ["nuvemshop"],
    },
    "salario-analista-ecommerce": {
        "nome": "Salário Analista Ecommerce",
        "cor_hex": "#737373",
        "legacy_slugs": [],
    },
}


def padronizar_categorias(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("finance", "CategoriaFinanceira")
    LancamentoFinanceiro = apps.get_model("finance", "LancamentoFinanceiro")

    categorias_destino = {}
    for slug, dados in TARGET_CATEGORIES.items():
        categoria, _ = CategoriaFinanceira.objects.update_or_create(
            slug=slug,
            defaults={
                "nome": dados["nome"],
                "cor_hex": dados["cor_hex"],
                "ativo": True,
            },
        )
        categorias_destino[slug] = categoria

    for slug, dados in TARGET_CATEGORIES.items():
        destino = categorias_destino[slug]
        for legacy_slug in dados["legacy_slugs"]:
            LancamentoFinanceiro.objects.filter(
                categoria__slug=legacy_slug,
            ).update(categoria=destino)

    CategoriaFinanceira.objects.exclude(
        slug__in=TARGET_CATEGORIES.keys(),
    ).update(ativo=False)


def reativar_categorias(apps, schema_editor):
    CategoriaFinanceira = apps.get_model("finance", "CategoriaFinanceira")
    CategoriaFinanceira.objects.all().update(ativo=True)


class Migration(migrations.Migration):
    dependencies = [
        ("finance", "0002_lancamento_pagamento_trafego"),
    ]

    operations = [
        migrations.RunPython(padronizar_categorias, reativar_categorias),
    ]
