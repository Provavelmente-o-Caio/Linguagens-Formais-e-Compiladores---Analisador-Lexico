from typing import List, Tuple

from src.gramaticas import Gramatica, NaoTerminal, Terminal
from src.ll.tabela_ll1 import TabelaLL1


class ParserLL1:
    def __init__(self, tabela: TabelaLL1, gramatica: Gramatica) -> None:
        self.tabela = tabela
        self.gramatica = gramatica
        self.derivacao: List[str] = []

    def parsear(self, tokens: List[Tuple[str, str]]) -> bool:
        pilha: list[Terminal | NaoTerminal | str] = [
            Terminal("$"),
            self.gramatica.simbolo_inicial,
        ]
        simbolo: list[Terminal | NaoTerminal] = []
        entrada = [(lexema, tipo) for lexema, tipo in tokens]
        if not entrada or entrada[-1][1] not in ["$", "EOF"]:
            entrada.append(("$", "$"))  # Fim de entrada

        posicao = 0
        passo = 0
        self.derivacao.clear()

        if self.tabela is None:
            raise RuntimeError(
                "Tabela LL(1) não inicializada. "
                "Atribua uma TabelaLL1 a ParserLL1.tabela antes de chamar parsear()."
            )

        while True:
            passo += 1

            # pega estado da pilha
            topo = pilha[-1]

            # simbolo atual
            _, tipo_atual = entrada[posicao]
            simbolo_atual = Terminal(tipo_atual)

            # Ambos $
            if simbolo_atual == Terminal("$") and topo == Terminal("$"):
                return True  # Aceita a entrada

            if isinstance(topo, Terminal):
                if topo == simbolo_atual:
                    pilha.pop()  # Desempilha terminal
                    posicao += 1  # Avança na entrada
                else:
                    # Terminal Errado
                    print(
                        f"Erro de sintaxe: esperado '{topo.nome}', encontrado '{simbolo_atual.nome}' no passo {passo}."
                    )
                    return False

            if isinstance(topo, NaoTerminal):
                producao = self.tabela.consultar(topo, simbolo_atual)

                if not producao:
                    print(
                        f"Erro de sintaxe: não há produção para {topo} com símbolo de entrada '{simbolo_atual.nome}' no passo {passo}."
                    )
                    return False

                pilha.pop()  # Desempilha o não-terminal
                corpo = producao.corpo

                self.derivacao.append(str(producao))

                for simbolo in reversed(corpo):
                    pilha.append(simbolo)
            else:
                print(
                    f"Erro de sintaxe: símbolo não reconhecido '{simbolo_atual.nome}' no passo {passo}."
                )
                return False

    def imprimir_derivacao(self):
        """Imprime as produções usadas (derivação mais à esquerda)."""
        if not self.derivacao:
            print("Nenhuma derivação disponível (execute parsear() primeiro).")
            return

        print("\n=== DERIVAÇÃO (Leftmost) ===\n")
        for i, producao in enumerate(self.derivacao, 1):
            print(f"{i:3}. {producao}")
