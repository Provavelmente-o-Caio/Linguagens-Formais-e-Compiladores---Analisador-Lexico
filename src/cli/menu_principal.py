from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from src.analizador_lexico import AnalizadorLexico
from src.cli.projeto import tela_projeto
from src.cli.execucao import tela_execucao

console = Console()

def iniciar_cli():
    analisador = AnalizadorLexico()

    # tenta carregar definições de um arquivo padrão se existir
    try:
        analisador.ler_entradas("tests/input_exemplo_2.txt")
    except FileNotFoundError:
        pass

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Gerador de Analisadores Léxicos[/bold cyan]", expand=False))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Projeto do analisador (criar ERs, gerar AFDs, minimizar, visualizar)")
        table.add_row("2", "Execução do analisador (analisar arquivo/texto e exportar tokens)")
        table.add_row("3", "Carregar definições de arquivo (tests/input_exemplo_2.txt)")
        table.add_row("0", "Sair")

        console.print(table)

        escolha = Prompt.ask("\n[bold green]Selecione uma opção[/bold green]", choices=["0","1","2","3"], default="1")

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
            console.print("[yellow]Saindo...[/yellow]")
            break
