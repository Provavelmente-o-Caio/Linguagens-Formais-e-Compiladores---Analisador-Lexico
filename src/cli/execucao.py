from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from rich.table import Table
from src.automatos import HandlerAutomatos

console = Console()
handler = HandlerAutomatos()

def tela_execucao(analisador):
    while True:
        console.clear()
        console.print(Panel("[bold magenta]Execução do Analisador[/bold magenta]"))

        table = Table(show_header=False, box=None)
        table.add_column("Opção", justify="center", width=6)
        table.add_column("Descrição")

        table.add_row("1", "Carregar arquivo de texto fonte")
        table.add_row("2", "Analisar texto carregado")
        table.add_row("3", "Listar tokens gerados")
        table.add_row("4", "Exportar tokens para arquivo")
        table.add_row("0", "Voltar")

        console.print(table)
        op = Prompt.ask("\nSelecione", choices=["0","1","2","3","4"], default="0")

        if op == "1":
            path = Prompt.ask("Caminho do arquivo (ex: tests/input_exemplo_1.txt)")
            if not path:
                path = "tests/input_exemplo_1.txt"
            try:
                with open(path, "r", encoding="utf-8") as f:
                    analisador.entrada_texto = f.read()
                console.print(f"[green]Arquivo '{path}' carregado![/green]")
            except Exception as e:
                console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "2":
            if not getattr(analisador, "entrada_texto", None):
                console.print("[yellow]Nenhum texto carregado. Carregue um arquivo primeiro.[/yellow]")
                input("ENTER para continuar...")
                continue
            # requer que o analisador possua um método para executar usando a tabela léxica
            # WIP
            pass
        elif op == "3":
            tokens = getattr(analisador, "ultima_lista_tokens", None)
            if not tokens:
                console.print("[yellow]Nenhuma lista de tokens disponível. Execute a análise primeiro.[/yellow]")
            else:
                table = Table(title="Tokens Encontrados", show_header=True)
                table.add_column("Lexema")
                table.add_column("Padrão / Observação")
                for lex, pad in tokens:
                    table.add_row(str(lex), str(pad))
                console.print(table)
            input("ENTER para continuar...")
        elif op == "4":
            tokens = getattr(analisador, "ultima_lista_tokens", None)
            if not tokens:
                console.print("[yellow]Nenhuma lista de tokens para exportar.[/yellow]")
                input("ENTER para continuar...")
                continue
            path = Prompt.ask("Nome do arquivo de saída", default="saida_tokens.txt")
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for lex, pad in tokens:
                        f.write(f"<{lex},{pad}>\n")
                console.print(f"[green]Tokens exportados para {path}[/green]")
            except Exception as e:
                console.print(f"[red]Erro ao exportar: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "0":
            return
