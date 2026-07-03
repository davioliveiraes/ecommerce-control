"""
Cria a empresa legada para o usuário administrador existente e atribui a ela
todos os dados criados antes do sistema virar multi-tenant.

O CNPJ é um placeholder (zeros) — ajustar depois no Django Admin.
"""

from django.db import migrations

CNPJ_PLACEHOLDER = "00000000000000"

MODELOS_ESCOPADOS = [
    ("catalog", "Marca"),
    ("catalog", "Categoria"),
    ("catalog", "Subcategoria"),
    ("catalog", "Produto"),
    ("finance", "CategoriaFinanceira"),
    ("finance", "LancamentoFinanceiro"),
    ("finance", "VisaoGeralPeriodo"),
]


def criar_empresa_legada(apps, schema_editor):
    User = apps.get_model("auth", "User")
    Empresa = apps.get_model("accounts", "Empresa")

    dono = User.objects.filter(is_superuser=True).order_by("id").first()
    if dono is None:
        return

    empresa, _ = Empresa.objects.get_or_create(
        user=dono,
        defaults={"nome": "Ibeize", "cnpj": CNPJ_PLACEHOLDER},
    )

    for app_label, model_name in MODELOS_ESCOPADOS:
        Model = apps.get_model(app_label, model_name)
        Model.objects.filter(empresa__isnull=True).update(empresa=empresa)


def reverter(apps, schema_editor):
    Empresa = apps.get_model("accounts", "Empresa")
    Empresa.objects.filter(cnpj=CNPJ_PLACEHOLDER).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
        ("catalog", "0011_categoria_empresa_marca_empresa_produto_empresa_and_more"),
        ("finance", "0004_categoriafinanceira_empresa_and_more"),
    ]

    operations = [
        migrations.RunPython(criar_empresa_legada, reverter),
    ]
