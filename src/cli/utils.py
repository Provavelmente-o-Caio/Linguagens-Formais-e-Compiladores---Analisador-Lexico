import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt

console = Console()


def selecionar_arquivo_definicao(analisador):
    pasta = "tests/arquivos_definicao"

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de definições[/bold cyan]"))

        try:
            arquivos = sorted([
                f for f in os.listdir(pasta)
                if os.path.isfile(os.path.join(pasta, f))
            ])
        except FileNotFoundError:
            console.print(f"[red]Pasta não encontrada: {pasta}[/red]")
            input("ENTER para voltar...")
            return

        if not arquivos:
            console.print("[red]Nenhum arquivo encontrado na pasta de definições![/red]")
            input("ENTER para voltar...")
            return

        tabela = Table(show_header=True, header_style="bold blue", expand=True)
        tabela.add_column("Índice", justify="center")
        tabela.add_column("Arquivo")

        for idx, nome in enumerate(arquivos, start=1):
            tabela.add_row(str(idx), nome)

        console.print(tabela)

        escolha = Prompt.ask(
            "\n[bold green]Digite o índice do arquivo para carregar[/bold green]"
        )

        if not escolha.isdigit():
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")
            continue

        idx = int(escolha)

        if idx < 1 or idx > len(arquivos):
            console.print("[red]Opção inválida![/red]")
            input("Pressione ENTER para tentar novamente...")
            continue

        arquivo_escolhido = os.path.join(pasta, arquivos[idx - 1])

        try:
            analisador.ler_definicoes(arquivo_escolhido)
            console.print(f"[green]Definições carregadas de {arquivo_escolhido}[/green]")
            input("ENTER para continuar...")
            return
        except Exception as e:
            console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para tentar novamente...")


def selecionar_arquivo_entrada(analisador):
    pasta = "tests/arquivos_entrada"

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de entrada[/bold cyan]"))

        try:
            arquivos = sorted([
                f for f in os.listdir(pasta)
                if os.path.isfile(os.path.join(pasta, f))
            ])
        except FileNotFoundError:
            console.print(f"[red]Pasta não encontrada: {pasta}[/red]")
            input("ENTER para voltar...")
            return

        if not arquivos:
            console.print("[red]Nenhum arquivo encontrado na pasta de entrada![/red]")
            input("ENTER para voltar...")
            return

        tabela = Table(show_header=True, header_style="bold blue", expand=True)
        tabela.add_column("Opções", justify="center")
        tabela.add_column("Arquivo")

        for idx, nome in enumerate(arquivos, start=1):
            tabela.add_row(str(idx), nome)

        console.print(tabela)

        escolha = Prompt.ask(
            "\n[bold green]Digite a opção do arquivo para carregar[/bold green]"
        )

        if not escolha.isdigit():
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")
            continue

        idx = int(escolha)

        if idx < 1 or idx > len(arquivos):
            console.print("[red]Opção inválida![/red]")
            input("Pressione ENTER para tentar novamente...")
            continue

        arquivo_escolhido = os.path.join(pasta, arquivos[idx - 1])

        try:
            with open(arquivo_escolhido, "r", encoding="utf-8") as f:
                analisador.entrada_texto = f.read().splitlines()
            console.print(f"[green]Arquivo '{arquivo_escolhido}' carregado![/green]")
            input("Pressione ENTER para continuar...")
            return
        except Exception as e:
            console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para continuar...")


def selecionar_arquivo_saida(analisador):
    pasta = Path(__file__).resolve().parent.parent.parent / "tests/arquivos_saida"

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de saída[/bold cyan]"))

        # garante que a pasta existe
        pasta.mkdir(parents=True, exist_ok=True)

        # lista arquivos existentes
        arquivos = sorted([
            f for f in os.listdir(pasta)
            if os.path.isfile(pasta / f)
        ])

        tabela = Table(show_header=True, header_style="bold blue", expand=True)
        tabela.add_column("Índice", justify="center")
        tabela.add_column("Ação / Arquivo")

        tabela.add_row("1", "[yellow]Não definir arquivo de saída[/yellow]")
        tabela.add_row("2", "[green]Criar novo arquivo de saída[/green]")

        for idx, nome in enumerate(arquivos, start=3):
            tabela.add_row(str(idx), nome)

        console.print(tabela)

        escolha = Prompt.ask(
            "\n[bold green]Digite a opção desejada[/bold green]"
        )

        if not escolha.isdigit():
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")
            continue

        idx = int(escolha)

        if idx == 1:
            analisador.arquivo_saida = None
            console.print("[yellow]Nenhum arquivo de saída definido[/yellow]")
            input("ENTER para continuar...")
            return

        if idx == 2:
            nome = Prompt.ask("[bold green]Nome do novo arquivo[/bold green]")

            if not nome.strip():
                console.print("[red]Nome inválido![/red]")
                input("ENTER para tentar novamente...")
                continue

            caminho = pasta / nome

            try:
                # cria arquivo vazio
                with open(caminho, "w", encoding="utf-8"):
                    pass
                analisador.arquivo_saida = caminho
                console.print(f"[green]Arquivo de saída criado: {caminho}[/green]")
                input("ENTER para continuar...")
                return

            except Exception as e:
                console.print(f"[red]Erro ao criar arquivo: {e}[/red]")
                input("ENTER para tentar novamente...")
                continue

        if 3 <= idx < 3 + len(arquivos):
            nome = arquivos[idx - 3]
            caminho = pasta / nome
            analisador.arquivo_saida = caminho
            console.print(f"[green]Arquivo selecionado: {caminho}[/green]")
            input("ENTER para continuar...")
            return
        else:
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")
