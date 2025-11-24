from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.automatos import HandlerAutomatos
from .utils import (
    selecionar_arquivo_gramatica,
    selecionar_arquivo_saida,
    mostrar_gramatica,
    mostrar_tabela_simbolos,
    mostrar_resultado_slr,
)


console = Console()
handler = HandlerAutomatos()


def interface_sintatico_projeto(analisador_sintatico):
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Projeto do Analisador Sintático[/bold cyan]"))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Selecionar arquivo de gramática")
        table.add_row("2", "Mostrar gramática carregada")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2"],
            default="0",
        )

        if escolha == "1":
            selecionar_arquivo_gramatica(analisador_sintatico)
        elif escolha == "2":
            mostrar_gramatica(analisador_sintatico.gramatica)
        elif escolha == "0":
            return


def interface_sintatico_execucao(analisador_sintatico):
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold bright_cyan]Execução do Analisador Sintático[/bold bright_cyan]"
            )
        )

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Selecionar arquivo de entrada (tokens)")
        table.add_row("2", "Executar analisador sintático")
        table.add_row("3", "Mostrar tabela de símbolos")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2", "3"],
            default="0",
        )

        if escolha == "1":
            selecionar_arquivo_saida(analisador_sintatico)
        elif escolha == "2":
            if not analisador_sintatico.arquivo_tokens:
                console.print("[red]Nenhum arquivo de tokens selecionado![/red]")
                input("ENTER para continuar...")
                continue
            if not analisador_sintatico.gramatica:
                console.print("[red]Nenhuma gramática carregada![/red]")
                input("ENTER para continuar...")
                continue
            resultado, handler, analisador_slr, parser = analisador_sintatico.analisar(
                analisador_sintatico.arquivo_tokens, completo=True
            )
            mostrar_resultado_slr(handler, analisador_slr, parser, resultado)
        elif escolha == "3":
            if not getattr(analisador_sintatico, "tabela_simbolos", None):
                console.print("[red]Tabela de símbolos ainda não foi gerada, execute o analisador sintático primeiro![/red]")
                input("ENTER para continuar...")
                continue
            mostrar_tabela_simbolos(analisador_sintatico.tabela_simbolos)
        elif escolha == "0":
            return
