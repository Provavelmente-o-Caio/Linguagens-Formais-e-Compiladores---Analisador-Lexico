from rich.console import Console
from rich.prompt import Prompt
from rich.table import Table
from rich.panel import Panel
from src.expressaoregular import ExpressaoRegular
from src.automatos import HandlerAutomatos

console = Console()
handler = HandlerAutomatos()

def tela_projeto(analisador):
    while True:
        console.clear()
        console.print(Panel("[bold cyan]Projeto do Analisador[/bold cyan]"))

        table = Table(show_header=False, box=None)
        table.add_column("Opção", justify="center", width=6)
        table.add_column("Descrição")

        table.add_row("", "[bold cyan]Definições[/bold cyan]")
        table.add_row("1", "Listar definições")
        table.add_row("2", "Adicionar expressão regular")
        table.add_row("3", "[bold]Gerar analisador léxico[/bold]")
        table.add_row("", "")
        table.add_row("", "[bold cyan]Execução em Passos[/bold cyan]")
        table.add_row("4", "Gerar AFDs (para todas as ERs)")
        table.add_row("5", "Minimizar AFDs")
        table.add_row("6", "Unir AFDs via ε")
        table.add_row("7", "Determinizar (autômato unido)")
        table.add_row("", "")
        table.add_row("", "[bold cyan]Tabelas[/bold cyan]")
        table.add_row("8", "Visualizar tabelas de transição")
        table.add_row("", "")
        table.add_row("[red]0[/red]", "Voltar")

        console.print(table)

        op = Prompt.ask("\nSelecione", choices=[str(i) for i in range(0,9)], default="0")

        if op == "1":
            if not analisador.definicoes:
                console.print("[yellow]Nenhuma definição cadastrada.[/yellow]")
            else:
                table = Table(title="Definições", show_header=True, header_style="bold magenta")
                table.add_column("Nome")
                table.add_column("Expressão Regular")
                for nome, er in analisador.definicoes.items():
                    table.add_row(nome, er)
                console.print(table)
            input("ENTER para continuar...")
        elif op == "2":
            nome = Prompt.ask("Nome da definição (ex: id)")
            er = Prompt.ask("Expressão regular (use [a-zA-Z], *, +, ?, |, & para ε)")
            analisador.definicoes[nome] = er
            console.print(f"[green]ER '{nome}' adicionada![/green]")
            input("ENTER para continuar...")
        elif op == "3":
            try:
                analisador.gerar_analisador()
                console.print("[green]Analisador léxico gerado com sucesso![/green]")
            except Exception as e:
                console.print(f"[red]Erro ao gerar analisador: {e}[/red]")
            input("ENTER para continuar...")
        
        elif op == "4":
            if not analisador.definicoes:
                console.print("[red]Não há definições para gerar AFDs.[/red]")
            else:
                analisador.afds = {}
                for nome, er in analisador.definicoes.items():
                    try:
                        expr = ExpressaoRegular(er)
                        afd = analisador.conversor.gerar_afd(expr)
                        analisador.afds[nome] = afd
                        console.print(f"[green]Gerado AFD para '{nome}'[/green]")
                    except Exception as e:
                        console.print(f"[red]Erro gerando AFD para {nome}: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "5":
            if getattr(analisador, "afds", None):
                analisador.afds_min = {}
                for nome, afd in analisador.afds.items():
                    try:
                        min_afd = handler.minimizar(afd)
                        analisador.afds_min[nome] = min_afd
                        console.print(f"[green]Minimizado: {nome}[/green]")
                    except Exception as e:
                        console.print(f"[red]Erro ao minimizar {nome}: {e}[/red]")
            else:
                console.print("[yellow]Primeiro gere os AFDs (opção 4).[/yellow]")
            input("ENTER para continuar...")
        elif op == "6":
            # unir todos AFDs (se existirem) criando um AFN via ε
            afds = getattr(analisador, "afds_min", None) or getattr(analisador, "afds", None)
            if not afds:
                console.print("[yellow]Nenhum AFD disponível para unir. Gere AFDs primeiro.[/yellow]")
                input("ENTER para continuar...")
                continue
            try:
                auts = list(afds.values())
                result = auts[0]
                for a in auts[1:]:
                    result = handler.uniao(result, a)
                analisador.afn_unido = result
                console.print("[green]Autômatos unidos via ε com sucesso.[/green]")
            except Exception as e:
                console.print(f"[red]Erro ao unir autômatos: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "7":
            if not getattr(analisador, "afn_unido", None):
                console.print("[yellow]Primeiro una os autômatos (opção 6).[/yellow]")
            else:
                try:
                    afd_unido = handler.determinizar(analisador.afn_unido)
                    analisador.afd_unido = afd_unido
                    console.print("[green]Determinização realizada com sucesso.[/green]")
                except Exception as e:
                    console.print(f"[red]Erro ao determinizar: {e}[/red]")
            input("ENTER para continuar...")
        elif op == "8":
            # imprime tabelas existentes: AFDs individuais e o unido/determinizado
            from rich.box import SQUARE

            if getattr(analisador, "afds", None):
                for nome, afd in analisador.afds.items():
                    console.print(Panel(f"[bold cyan]AFD: {nome}[/bold cyan]"))
                    table = Table(
                        title=f"Tabela de Transição — {nome}",
                        box=SQUARE,
                        header_style="bold magenta",
                        expand=True
                    )
                    
                    # Cabeçalho: Estado + cada símbolo
                    table.add_column("Estado", justify="center", style="bold")

                    simbolos_ord = sorted(afd.simbolos)

                    for s in simbolos_ord:
                        table.add_column(s, justify="center")

                    # Ordenar estados
                    estados_ord = sorted(afd.estados, key=lambda e: e.nome)

                    # Montar linhas
                    for estado in estados_ord:

                        marcador = ""
                        if estado == afd.estado_inicial:
                            marcador += "→ "
                        if estado in afd.estados_finais:
                            marcador += "*"

                        nome_estado = f"{marcador}{estado.nome}"

                        linha = [nome_estado]

                        for s in simbolos_ord:
                            destinos = afd.transicoes.get((estado, s), set())
                            if destinos:
                                destinos_str = ", ".join(sorted(d.nome for d in destinos))
                                linha.append(destinos_str)
                            else:
                                linha.append("-")

                        table.add_row(*linha)

                    console.print(table)

            if getattr(analisador, "afd_unido", None):
                afd = analisador.afd_unido
                console.print(Panel("[bold cyan]AFD unificado por etapas[/bold cyan]"))

                table = Table(
                    title="Tabela de Transição — AFD Unificado",
                    box=SQUARE,
                    header_style="bold magenta",
                    expand=True
                )

                table.add_column("Estado", justify="center", style="bold")
                simbolos_ord = sorted(afd.simbolos)

                for s in simbolos_ord:
                    table.add_column(s, justify="center")

                estados_ord = sorted(afd.estados, key=lambda e: e.nome)

                for estado in estados_ord:
                    marcador = ""
                    if estado == afd.estado_inicial:
                        marcador += "→ "
                    if estado in afd.estados_finais:
                        marcador += "*"

                    nome_estado = f"{marcador}{estado.nome}"
                    linha = [nome_estado]

                    for s in simbolos_ord:
                        destinos = afd.transicoes.get((estado, s), set())
                        if destinos:
                            destinos_str = ", ".join(sorted(d.nome for d in destinos))
                            linha.append(destinos_str)
                        else:
                            linha.append("-")

                    table.add_row(*linha)

                console.print(table)

            if getattr(analisador, "automato_unificado", None):
                console.print(Panel("[bold cyan]AFD unificado por gerador[/bold cyan]"))
                afd = analisador.automato_unificado

                table = Table(
                    title="Tabela de Transição — AFD Unificado",
                    box=SQUARE,
                    header_style="bold magenta",
                    expand=True
                )

                table.add_column("Estado", justify="center", style="bold")
                simbolos_ord = sorted(afd.simbolos)
                for s in simbolos_ord:
                    table.add_column(s, justify="center")

                estados_ord = sorted(afd.estados, key=lambda e: e.nome)
                for estado in estados_ord:
                    marcador = ""
                    if estado == afd.estado_inicial:
                        marcador += "→ "
                    if estado in afd.estados_finais:
                        marcador += "*"

                    nome_estado = f"{marcador}{estado.nome}"
                    linha = [nome_estado]

                    for s in simbolos_ord:
                        destinos = afd.transicoes.get((estado, s), set())
                        if destinos:
                            destinos_str = ", ".join(sorted(d.nome for d in destinos))
                            linha.append(destinos_str)
                        else:
                            linha.append("-")

                    table.add_row(*linha)

                console.print(table)

            input("ENTER para continuar...")

        elif op == "0":
            return
        else:
            console.print("[red]Opção inválida[/red]")
            input("ENTER para continuar...")
