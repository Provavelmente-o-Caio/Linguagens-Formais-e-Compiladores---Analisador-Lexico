import os
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt
from typing import Any

console = Console()


def selecionar_arquivo_definicao(analisador):
    pasta = "tests/arquivos_definicao"

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de definições[/bold cyan]"))

        try:
            arquivos = sorted(
                [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
            )
        except FileNotFoundError:
            console.print(f"[red]Pasta não encontrada: {pasta}[/red]")
            input("ENTER para voltar...")
            return

        if not arquivos:
            console.print(
                "[red]Nenhum arquivo encontrado na pasta de definições![/red]"
            )
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

        # escolha = "1"

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
            console.print(
                f"[green]Definições carregadas de {arquivo_escolhido}[/green]"
            )
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
            arquivos = sorted(
                [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
            )
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

        # escolha = "1"

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
    pasta = (
        Path(__file__).resolve().parent.parent.parent / "tests/arquivos_saida_tokens"
    )

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de Tokens[/bold cyan]"))

        # garante que a pasta existe
        pasta.mkdir(parents=True, exist_ok=True)

        # lista arquivos existentes
        arquivos = sorted([f for f in os.listdir(pasta) if os.path.isfile(pasta / f)])

        tabela = Table(show_header=True, header_style="bold blue", expand=True)
        tabela.add_column("Opções", justify="center")
        tabela.add_column("Ação / Arquivo")

        tabela.add_row("1", "[yellow]Não definir arquivo de saída para tokens[/yellow]")
        tabela.add_row("2", "[green]Criar novo arquivo de saída para tokens[/green]")

        for idx, nome in enumerate(arquivos, start=3):
            tabela.add_row(str(idx), nome)

        console.print(tabela)

        escolha = Prompt.ask("\n[bold green]Digite a opção desejada[/bold green]")

        # escolha = "1"

        if not escolha.isdigit():
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")
            continue

        idx = int(escolha)

        if idx == 1:
            analisador.arquivo_tokens = None
            console.print(
                "[yellow]Nenhum arquivo de saída para tokens definido[/yellow]"
            )
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
                analisador.arquivo_tokens = caminho
                console.print(
                    f"[green]Arquivo de saída para tokens criado: {caminho}[/green]"
                )
                return

            except Exception as e:
                console.print(f"[red]Erro ao criar arquivo: {e}[/red]")
                input("ENTER para tentar novamente...")
                continue

        if 3 <= idx < 3 + len(arquivos):
            nome = arquivos[idx - 3]
            caminho = pasta / nome
            analisador.arquivo_tokens = caminho
            console.print(f"[green]Arquivo selecionado: {caminho}[/green]")
            input("ENTER para continuar...")
            return
        else:
            console.print("[red]Opção inválida![/red]")
            input("ENTER para tentar novamente...")


def selecionar_arquivo_gramatica(analisador):
    pasta = "tests/arquivos_gramatica"

    while True:
        console.clear()
        console.print(Panel("[bold cyan]Selecionar arquivo de gramática[/bold cyan]"))

        try:
            arquivos = sorted(
                [f for f in os.listdir(pasta) if os.path.isfile(os.path.join(pasta, f))]
            )
        except FileNotFoundError:
            console.print(f"[red]Pasta não encontrada: {pasta}[/red]")
            input("ENTER para voltar...")
            return

        if not arquivos:
            console.print("[red]Nenhum arquivo encontrado na pasta de gramática![/red]")
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
            analisador.ler_gramatica(arquivo_escolhido)
            console.clear()
            mostrar_gramatica(analisador.gramatica)
            return
        except Exception as e:
            console.print(f"[red]Erro ao carregar arquivo: {e}[/red]")
            input("Pressione ENTER para tentar novamente...")


def mostrar_gramatica(gramatica):
    if not gramatica:
        console.print("[red]Nenhuma gramática foi carregada ainda.[/red]")
        input("\nENTER para continuar...")
        return

    console.clear()
    console.print(
        Panel("[bold bright_cyan]Gramática Carregada[/bold bright_cyan]", expand=False)
    )

    console.print(
        f"[bold green]Símbolo inicial:[/bold green] [bright_cyan]{gramatica.simbolo_inicial}[/bright_cyan]\n"
    )

    table_prod = Table(title="Produções", header_style="bold blue", show_lines=True)
    table_prod.add_column("Nº", justify="center")
    table_prod.add_column("Produção")

    for p in gramatica.producoes:
        corpo = " ".join(str(s) for s in p.corpo)
        table_prod.add_row(
            str(p.numero),
            f"[bright_cyan]{p.cabeca}[/bright_cyan] [white]::=[/white] {corpo}",
        )

    console.print(table_prod)
    console.print()

    table_nt = Table(header_style="bold blue", expand=False)
    table_nt.add_column("Não-terminais", justify="center")

    for nt in sorted([str(x) for x in gramatica.nao_terminais]):
        table_nt.add_row(f"[white]{nt}[/white]")

    console.print(table_nt)
    console.print()

    table_t = Table(header_style="bold blue", expand=False)
    table_t.add_column("Terminais", justify="center")

    for t in sorted([str(x) for x in gramatica.terminais]):
        table_t.add_row(f"[white]{t}[/white]")

    console.print(table_t)
    console.print()

    input("\nENTER para continuar...")


def mostrar_tabela_simbolos(tabela_simbolos):
    console.clear()
    console.print(Panel("[bold cyan]Tabela de Símbolos[/bold cyan]", expand=False))

    if not tabela_simbolos.tabela:
        console.print("[red]A tabela de símbolos está vazia![/red]")
        input("\nENTER para continuar...")
        return

    tabela = Table(
        show_header=True, header_style="bold yellow", show_lines=True, expand=False
    )

    tabela.add_column("Pos", justify="center", style="green", no_wrap=True)
    tabela.add_column("Lexema", style="white")
    tabela.add_column("Categoria", justify="center", style="white")
    tabela.add_column("Tipo", justify="center", style="white")
    tabela.add_column("Escopo", justify="center", style="white")

    entradas = sorted(tabela_simbolos.tabela.values(), key=lambda e: e.posicao)

    for e in entradas:
        tabela.add_row(
            str(e.posicao),
            str(e.lexema),
            str(e.categoria),
            str(e.tipo or "-"),
            str(e.escopo or "-"),
        )

    console.print(tabela)

    stats = tabela_simbolos.estatisticas()

    console.print()
    console.print(
        Panel("[bold cyan]Estatísticas da Tabela de Símbolos[/bold cyan]", expand=False)
    )

    tabela_stats = Table(
        show_header=True, header_style="bold yellow", show_lines=True, expand=False
    )

    tabela_stats.add_column("Categoria", justify="center", style="white")
    tabela_stats.add_column("Quantidade", justify="center", style="white")

    for categoria, qtd in stats.items():
        tabela_stats.add_row(str(categoria), str(qtd))

    console.print(tabela_stats)

    input("\nENTER para continuar...")


def _safe_get(obj: Any, *attrs, default=None):
    """Tenta obter encadeamento de atributos/dicionários de forma segura."""
    cur = obj
    for a in attrs:
        if cur is None:
            return default
        # primeiro, tentar como atributo
        if hasattr(cur, a):
            cur = getattr(cur, a)
            continue
        # segundo, tentar como chave dict
        try:
            cur = cur[a]  # type: ignore
            continue
        except Exception:
            return default
    return cur


def mostrar_resultado_slr(handler, analisador_slr, parser, resultado):
    console.clear()
    console.print(
        Panel(
            "[bold cyan]Resultado da Execução SLR[/bold cyan]",
            expand=False,
            border_style="cyan",
        )
    )

    first_cache = getattr(handler, "first_cache", None) or {}
    follow_cache = getattr(handler, "follow_cache", None) or {}

    # Tabela FIRST
    tabela_first = Table(
        title="FIRST", header_style="bold blue", show_lines=True, expand=False
    )
    tabela_first.add_column("Símbolo", style="bright_cyan")
    tabela_first.add_column("FIRST", style="white")
    if first_cache:
        for s, conj in first_cache.items():
            try:
                itens = ", ".join(sorted(str(x) for x in conj))
            except Exception:
                itens = ", ".join(str(x) for x in conj)
            tabela_first.add_row(str(s), itens)
    else:
        tabela_first.add_row("-", "FIRST não disponível")

    # Tabela FOLLOW
    tabela_follow = Table(
        title="FOLLOW", header_style="bold blue", show_lines=True, expand=False
    )
    tabela_follow.add_column("Não-terminal", style="bright_cyan")
    tabela_follow.add_column("FOLLOW", style="white")
    if follow_cache:
        for nt, conj in follow_cache.items():
            try:
                itens = ", ".join(sorted(str(x) for x in conj))
            except Exception:
                itens = ", ".join(str(x) for x in conj)
            tabela_follow.add_row(str(nt), itens)
    else:
        tabela_follow.add_row("-", "FOLLOW não disponível")

    console.print(tabela_first)
    console.print(tabela_follow)

    transicoes = getattr(analisador_slr, "transicoes", None)
    if transicoes:
        tabela_tr = Table(
            title="Transições (Ix --símbolo--> Iy)",
            header_style="bold blue",
            show_lines=True,
            expand=False,
        )
        tabela_tr.add_column("Origem", style="bright_cyan", justify="center")
        tabela_tr.add_column("Símbolo", style="white", justify="center")
        tabela_tr.add_column("Destino", style="bright_cyan", justify="center")

        for (origem, simbolo), destino in sorted(
            transicoes.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))
        ):
            tabela_tr.add_row(f"I{origem}", str(simbolo), f"I{destino}")
        console.print(tabela_tr)
    else:
        console.print(
            "[yellow]Transições não disponíveis (coleção/tabela não construída).[/yellow]"
        )

    console.print()
    if resultado:
        console.print(Panel("[bold green]SENTENÇA ACEITA[/bold green]", expand=False))
    else:
        console.print(Panel("[bold red]ERRO SINTÁTICO[/bold red]", expand=False))

    console.print()
    tabela_deriv = Table(
        title="Derivação (Rightmost)",
        header_style="bold blue",
        show_lines=True,
        expand=False,
    )
    tabela_deriv.add_column("#", style="bright_cyan", justify="center")
    tabela_deriv.add_column("Produção aplicada", style="white")
    deriv = getattr(parser, "derivacao", None)
    if deriv:
        for i, p in enumerate(deriv, 1):
            tabela_deriv.add_row(str(i), str(p))
    else:
        tabela_deriv.add_row("-", "Nenhuma derivação disponível")
    console.print(tabela_deriv)

    console.print()
    input("Pressione ENTER para continuar...")
