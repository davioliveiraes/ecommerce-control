from django.contrib import admin

from catalog.models import Categoria, Subcategoria, Produto, Variacao


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ativo", "criado_em")
    list_filter = ("ativo",)
    search_fields = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}


@admin.register(Subcategoria)
class SubcategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "categoria", "slug", "ativo")
    list_filter = ("ativo", "categoria")
    search_fields = ("nome", "slug", "categoria__nome")
    autocomplete_fields = ("categoria",)
    prepopulated_fields = {"slug": ("nome",)}


class VariacaoInline(admin.TabularInline):
    model = Variacao
    extra = 1
    fields = (
        "sku_nuvemshop", "descricao", "custo",
        "preco_loja", "preco_site", "preco_promocional",
        "status_nuvemshop", "status_integracao", "ativo",
    )
    show_change_link = True


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = ("nome_site", "categoria", "subcategoria", "ativo", "atualizado_em")
    list_filter = ("ativo", "categoria", "subcategoria")
    search_fields = ("nome_site", "nome_gestaoclick")
    autocomplete_fields = ("categoria", "subcategoria")
    inlines = [VariacaoInline]


@admin.register(Variacao)
class VariacaoAdmin(admin.ModelAdmin):
    list_display = (
        "sku_nuvemshop", "produto", "descricao",
        "custo", "preco_site", "margem_percentual_display",
        "preco_promocional", "margem_promocional_percentual_display",
        "status_nuvemshop", "ativo",
    )
    list_filter = ("ativo", "status_nuvemshop", "status_integracao", "produto__categoria")
    search_fields = (
        "sku_nuvemshop", "id_gestaoclick", "codigo_barras",
        "produto__nome_site", "produto__nome_gestaoclick",
    )
    autocomplete_fields = ("produto",)
    readonly_fields = ("criado_em", "atualizado_em")

    @admin.display(description="margem %")
    def margem_percentual_display(self, obj):
        if obj.margem_percentual is None:
            return "—"
        return f"{obj.margem_percentual:.1f}%"

    @admin.display(description="margem promoção %")
    def margem_promocional_percentual_display(self, obj):
        if obj.margem_promocional_percentual is None:
            return "—"
        return f"{obj.margem_promocional_percentual:.1f}%"
