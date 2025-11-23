from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from src.automatos import HandlerAutomatos

from .utils import selecionar_arquivo_entrada, selecionar_arquivo_saida

console = Console()
handler = HandlerAutomatos()


def tela_execucao(analisador):
    while True:
        console.clear()
        console.print(Panel("[bold magenta]Execução do Analisador[/bold magenta]"))

        table = Table(show_header=False, box=None)
        table.add_column("Opção", justify="center", width=6)
        table.add_column("Descrição")

        table.add_row("1", "Alterar arquivo de entrada")
        table.add_row("2", "Analisar texto carregado")
        table.add_row("3", "Listar tokens gerados")
        table.add_row("4", "Exportar tokens para arquivo de saída")
        table.add_row("0", "Voltar")

        console.print(table)
        op = Prompt.ask("\nSelecione", choices=["0", "1", "2", "3", "4"], default="0")

        if op == "1":
            selecionar_arquivo_entrada(analisador)
        elif op == "2":
            if not getattr(analisador, "entrada_texto", None):
                console.print(
                    "[yellow]Nenhum texto carregado. Carregue um arquivo primeiro.[/yellow]"
                )
                input("ENTER para continuar...")
                continue
            try:
                tokens = analisador.analisar()
                analisador.ultima_lista_tokens = tokens
                console.print(
                    f"[green]Análise concluída! {len(tokens)} tokens gerados.[/green]"
                )
            except Exception as e:
                console.print(f"[red]Erro durante a análise: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "3":
            tokens = getattr(analisador, "ultima_lista_tokens", None)
            if not tokens:
                console.print(
                    "[yellow]Nenhuma lista de tokens disponível. Execute a análise primeiro.[/yellow]"
                )
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

            output_path = analisador.arquivo_saida
            if not output_path:
                selecionar_arquivo_saida(analisador)
                output_path = analisador.arquivo_saida

            try:
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with output_path.open("w", encoding="utf-8") as f:
                    for token in tokens:
                        f.write(f"<{token[0]}, {token[1]}>\n")
                console.print(f"[green]Tokens exportados para {output_path}[/green]")
            except Exception as e:
                console.print(f"[red]Erro ao exportar: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "0":
            return
