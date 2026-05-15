"""Relatório de importação."""

from dataclasses import dataclass, field

from rich.console import Console
from rich.table import Table


@dataclass
class LinhaErro:
    linha_excel: int
    sku: str
    descricao: str
    erro: str


@dataclass
class RelatorioImport:
    total_linhas: int = 0
    produtos_criados: int = 0
    produtos_atualizados: int = 0
    variacoes_criadas: int = 0
    variacoes_atualizadas: int = 0
    linhas_puladas: int = 0
    erros: list[LinhaErro] = field(default_factory=list)
    dry_run: bool = False

    def registrar_erro(self, linha_excel: int, sku: str, descricao: str, erro: str):
        self.linhas_puladas += 1
        self.erros.append(LinhaErro(linha_excel, sku, descricao, erro))

    def imprimir(self, console: Console):
        modo = "[bold yellow]DRY-RUN[/bold yellow]" if self.dry_run else "[bold green]EXECUTADO[/bold green]"
        console.print(f"\n{modo}\n")

        resumo = Table(title="Resumo da Importação", header_style="bold cyan")
        resumo.add_column("Métrica", style="dim")
        resumo.add_column("Quantidade", justify="right")
        resumo.add_row("Total de linhas processadas", str(self.total_linhas))
        resumo.add_row("Produtos criados", str(self.produtos_criados))
        resumo.add_row("Produtos atualizados", str(self.produtos_atualizados))
        resumo.add_row("Variações criadas", str(self.variacoes_criadas))
        resumo.add_row("Variações atualizadas", str(self.variacoes_atualizadas))
        resumo.add_row("[red]Linhas puladas (erro)[/red]", f"[red]{self.linhas_puladas}[/red]")
        console.print(resumo)

        if self.erros:
            console.print()
            erros = Table(
                title=f"Linhas puladas ({len(self.erros)})",
                header_style="bold red",
            )
            erros.add_column("Linha Excel", justify="right")
            erros.add_column("SKU", style="dim")
            erros.add_column("Produto", max_width=40)
            erros.add_column("Erro", style="red")
            for e in self.erros:
                erros.add_row(str(e.linha_excel), e.sku or "—", e.descricao or "—", e.erro)
            console.print(erros)
