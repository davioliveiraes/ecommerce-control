from django.contrib import admin

from finance.models import CategoriaFinanceira, LancamentoFinanceiro


@admin.register(CategoriaFinanceira)
class CategoriaFinanceiraAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "cor_hex", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(LancamentoFinanceiro)
class LancamentoFinanceiroAdmin(admin.ModelAdmin):
    list_display = (
        "data_lancamento", "tipo", "descricao",
        "categoria", "valor", "status", "ativo",
    )
    list_filter = ("ativo", "tipo", "status", "categoria")
    search_fields = ("descricao", "observacoes")
    autocomplete_fields = ("categoria",)
    date_hierarchy = "data_lancamento"
