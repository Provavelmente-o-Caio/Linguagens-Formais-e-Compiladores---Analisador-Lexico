from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from src.analisador_lexico import AnalisadorLexico
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


def menu_lexico(analisador: AnalisadorLexico):
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Gerador de Analisadores Léxicos[/bold cyan]", expand=False))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Projeto do analisador (criar ERs, gerar AFDs, minimizar, visualizar)")
        table.add_row("2", "Execução do analisador (analisar arquivo/texto e exportar tokens)")
        table.add_row("0", "Voltar")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2"],
            default="0"
        )

        if escolha == "1":
            tela_projeto(analisador)
        elif escolha == "2":
            tela_execucao(analisador)

        elif escolha == "0":
            return


def iniciar_cli():
    analisador = AnalisadorLexico()

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de definições[/bold cyan]", expand=False))

        arquivo_definicoes = Prompt.ask(
            "\n[bold green]Caminho do arquivo de definições (Deixe vazio para padrão)[/bold green]"
        )
        if not arquivo_definicoes:
            arquivo_definicoes = "tests/input_basic_2.txt"
        try:
            analisador.ler_definicoes(arquivo_definicoes)
            console.print(f"[green]Definições carregadas de {arquivo_definicoes}[/green]")
            input("ENTER para continuar...")
            break
        except Exception as e:
            console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para tentar novamente...")
    

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de entrada[/bold cyan]", expand=False))

        arquivo_entrada = Prompt.ask(
            "\n[bold green]Caminho do arquivo de entrada (Deixe vazio para padrão)[/bold green]"
        )
        if not arquivo_entrada:
            arquivo_entrada = "tests/input_exemplo_2.txt"
        try:
            # tenta carregar o arquivo de entrada
            with open(arquivo_entrada, "r", encoding="utf-8") as f:
                analisador.entrada_texto = f.read()
            console.print(f"[green]Arquivo '{arquivo_entrada}' carregado![/green]")
            input("ENTER para continuar...")
            break
        except Exception as e:
            console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para tentar novamente...")

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de saída[/bold cyan]", expand=False))

        arquivo_saida = Prompt.ask(
            "\n[bold green]Caminho do arquivo de saída (Deixe vazio para nenhum)[/bold green]"
        )
        if arquivo_saida:
            project_root = Path(__file__).resolve().parent.parent.parent / "tests"
            output_path = project_root / arquivo_saida

            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)
                if output_path:
                    with open(output_path, "w", encoding="utf-8") as f:
                        pass  # apenas testa a abertura
                    analisador.arquivo_saida = output_path
                console.print(f"[green]Arquivo de saída definido: '{output_path}'[/green]")
                input("ENTER para continuar...")
                break
            except Exception as e:
                console.print(f"[red]Erro ao definir arquivo de saída: {e}[/red]")
                input("Pressione ENTER para tentar novamente...")
        else:
            arquivo_saida = None
            console.print("[green]Arquivo de saída não definido[/green]")
            input("ENTER para continuar...")
            break


    while True:
        console.clear()
        console.print(Panel("[bold cyan]Framework Gerador de Analisadores[/bold cyan]", expand=False))

        table = Table(show_header=True, header_style="bold blue", expand=True)
        table.add_column("Opção", justify="center")
        table.add_column("Descrição")

        table.add_row("1", "Gerador de Analisadores Léxicos")
        table.add_row("2", "Gerador de Analisadores Sintáticos (SLR)")
        table.add_row("3", "Carregar definições de arquivo")
        table.add_row("4", "Carregar arquivo de entrada")
        table.add_row("0", "Sair")

        console.print(table)

        escolha = Prompt.ask(
            "\n[bold green]Selecione uma opção[/bold green]",
            choices=["0", "1", "2", "3", "4"],
            default="0"
        )

        if escolha == "1":
            menu_lexico(analisador)
        elif escolha == "2":
            menu_sintatico()
        elif escolha == "3":
            path = Prompt.ask(
                "\n[bold green]Escolha o arquivo de definições (tests/input_basic_1.txt)[/bold green]"
            )
            if not path:
                path = "tests/input_basic_1.txt"
            try:
                analisador.ler_definicoes(path)
                console.print(f"[green]Definições carregadas de {path}[/green]")
            except Exception as e:
                console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para continuar...")
        elif escolha == "4":
            arquivo_entrada = Prompt.ask(
                "\n[bold green]Escolha o arquivo de entrada (tests/input_exemplo_1.txt)[/bold green]"
            )
            if not arquivo_entrada:
                arquivo_entrada = "tests/input_exemplo_1.txt"
            try:
                with open(arquivo_entrada, "r", encoding="utf-8") as f:
                    analisador.entrada_texto = f.read()
                console.print(f"[green]Arquivo '{arquivo_entrada}' carregado![/green]")
            except Exception as e:
                console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para continuar...")

        elif escolha == "0":
            console.print("[yellow]Saindo...[/yellow]")
            break
