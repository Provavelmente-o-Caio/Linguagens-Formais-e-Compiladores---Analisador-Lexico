from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from src.analizador_lexico import AnalizadorLexico
from src.cli.projeto import tela_projeto
from src.cli.execucao import tela_execucao

console = Console()

def menu_sintatico():
    while True:
        console.clear()
        console.print(Panel("[bold magenta]Gerador de Analisadores Sintáticos - SLR[/bold magenta]"))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Carregar gramática")
        table.add_row("2", "Mostrar produções")
        table.add_row("3", "Calcular FIRST e FOLLOW")
        table.add_row("4", "Gerar itens LR(0) (closure + goto)")
        table.add_row("5", "Gerar tabela SLR (ACTION/GOTO)")
        table.add_row("6", "Executar analisador sintático em tokens")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2", "3", "4", "5", "6"],
            default="0"
        )

        if escolha == "1":
            console.print("[yellow]WIP: Implementar leitura de gramática[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "2":
            console.print("[yellow]WIP: Mostrar gramática carregada[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "3":
            console.print("[yellow]WIP: FIRST e FOLLOW[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "4":
            console.print("[yellow]WIP: closure + goto + coleção LR(0)[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "5":
            console.print("[yellow]WIP: Tabela SLR[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "6":
            console.print("[yellow]WIP: Execução do analisador sintático[/yellow]")
            input("ENTER para continuar...")

        elif escolha == "0":
            break


def menu_lexico(analisador: AnalizadorLexico):
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Gerador de Analisadores Léxicos[/bold cyan]", expand=False))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Projeto do analisador (criar ERs, gerar AFDs, minimizar, visualizar)")
        table.add_row("2", "Execução do analisador (analisar arquivo/texto e exportar tokens)")
        table.add_row("3", "Carregar definições de arquivo (tests/input_exemplo_2.txt)")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2", "3"],
            default="0"
        )

        if escolha == "1":
            tela_projeto(analisador)
        elif escolha == "2":
            tela_execucao(analisador)
        elif escolha == "3":
            try:
                analisador.ler_entradas("tests/input_exemplo_2.txt")
                console.print("[green]Definições carregadas de tests/input_exemplo_2.txt[/green]")
            except Exception as e:
                console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para continuar...")

        elif escolha == "0":
            return


def iniciar_cli():
    analisador = AnalizadorLexico()

    # tenta carregar definições ao iniciar
    try:
        analisador.ler_entradas("tests/input_exemplo_2.txt")
    except FileNotFoundError:
        pass

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Framework Gerador de Analisadores[/bold cyan]", expand=False))

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
            default="0"
        )

        if escolha == "1":
            menu_lexico(analisador)

        elif escolha == "2":
            menu_sintatico()

        elif escolha == "0":
            console.print("[yellow]Saindo...[/yellow]")
            break
