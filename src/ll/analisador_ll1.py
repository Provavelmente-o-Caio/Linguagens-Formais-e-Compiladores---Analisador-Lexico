from typing import Optional

from src.gramaticas import Gramatica, HandlerGramatica
from src.ll.acoes import ConflictErrorLL1
from src.ll.tabela_ll1 import TabelaLL1


class AnalisadorLL1:
    def __init__(self, gramatica: Gramatica, handler: HandlerGramatica):
        self.gramatica = gramatica
        self.handler = handler
        self.tabela: Optional[TabelaLL1] = None

    def construir_tabela(self) -> TabelaLL1:
        self.tabela = TabelaLL1()

        try:
            self.tabela.construir(
                self.gramatica.producoes,
                self.handler,
            )
        except ConflictErrorLL1 as e:
            print(f"[AVISO] {e}")

        return self.tabela

    def imprimir_first_follow(self):
        """Imprime os conjuntos FIRST e FOLLOW de todos os não-terminais."""
        print("\n=== CONJUNTOS FIRST ===\n")
        for nt in sorted(self.gramatica.nao_terminais, key=str):
            first = self.handler.get_first(nt)
            print(
                f"  FIRST({nt}) = {{ {', '.join(str(s) for s in sorted(first, key=str))} }}"
            )

        print("\n=== CONJUNTOS FOLLOW ===\n")
        for nt in sorted(self.gramatica.nao_terminais, key=str):
            follow = self.handler.get_follow(nt)
            print(
                f"  FOLLOW({nt}) = {{ {', '.join(str(s) for s in sorted(follow, key=str))} }}"
            )
        print()
