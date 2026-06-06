from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from rich.console import Console

from importer.services.importer import ImportadorPlanilha


class Command(BaseCommand):
    help = "Importa produtos e variações de uma planilha xlsx para o catálogo."

    def add_arguments(self, parser):
        parser.add_argument("arquivo", type=str, help="Caminho para o arquivo .xlsx.")
        parser.add_argument("--dry-run", action="store_true", help="Simula sem alterar o banco.")

    def handle(self, *args, **options):
        caminho = Path(options["arquivo"]).expanduser().resolve()
        if not caminho.exists():
            raise CommandError(f"Arquivo não encontrado: {caminho}")
        if caminho.suffix.lower() != ".xlsx":
            raise CommandError(f"Arquivo deve ser .xlsx (encontrado: {caminho.suffix})")

        console = Console()
        dry_run = options["dry_run"]
        modo = "[bold yellow]DRY-RUN[/bold yellow]" if dry_run else "[bold green]EXECUÇÃO REAL[/bold green]"
        console.print(f"\n{modo} — Importando de [cyan]{caminho}[/cyan]\n")

        importador = ImportadorPlanilha(caminho=caminho, console=console, dry_run=dry_run)
        relatorio = importador.executar()
        relatorio.imprimir(console)

        if relatorio.linhas_puladas > 0:
            console.print(
                f"\n[yellow]Atenção: {relatorio.linhas_puladas} linhas foram puladas. "
                f"Verifique a tabela de erros e corrija a planilha se necessário.[/yellow]"
            )
