from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

from src.analisador_lexico import AnalisadorLexico
from src.analisador_sintatico import AnalisadorSintatico
from .cli_analisador_lexico import interface_lexico_projeto, interface_lexico_execucao
from .cli_analisador_sintatico import (
    interface_sintatico_projeto,
    interface_sintatico_execucao,
)
from .utils import (
    selecionar_arquivo_definicao,
    selecionar_arquivo_entrada,
    selecionar_arquivo_saida,
)

console = Console()


def menu_lexico(analisador: AnalisadorLexico):
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold cyan]Gerador de Analisadores Léxicos[/bold cyan]", expand=False
            )
        )

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row(
            "1",
            "Projeto do analisador léxico (criar ERs, gerar AFDs, minimizar, visualizar)",
        )
        table.add_row(
            "2",
            "Execução do analisador léxico (analisar arquivo/texto e exportar tokens)",
        )
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2"],
            default="0",
        )

        if escolha == "1":
            interface_lexico_projeto(analisador)
        elif escolha == "2":
            interface_lexico_execucao(analisador)
        elif escolha == "0":
            return


def menu_sintatico(analisador_sintatico: AnalisadorSintatico):
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold bright_cyan]Gerador de Analisadores Sintáticos - SLR[/bold bright_cyan]"
            )
        )

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Projeto do analisador sintático")
        table.add_row("2", "Execução do analisador sintático")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2"],
            default="0",
        )

        if escolha == "1":
            interface_sintatico_projeto(analisador_sintatico)
        elif escolha == "2":
            interface_sintatico_execucao(analisador_sintatico)
        elif escolha == "0":
            return


def iniciar_cli():
    analisador = AnalisadorLexico()
    analisador_sintatico = AnalisadorSintatico()

    while True:
        console.clear()
        console.print(
            Panel(
                "[bold cyan]Framework Gerador de Analisadores[/bold cyan]", expand=False
            )
        )

        # menu_sintatico(analisador_sintatico)
        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Gerador de Analisadores Léxicos")
        table.add_row("2", "Gerador de Analisadores Sintáticos (SLR)")
        table.add_row("0", "Sair")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2"],
            default="0",
        )

        if escolha == "1":
            menu_lexico(analisador)
        elif escolha == "2":
            menu_sintatico(analisador_sintatico)
        elif escolha == "0":
            console.print("[yellow]Saindo...[/yellow]")
            break
