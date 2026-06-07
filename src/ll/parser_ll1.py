from typing import List

from src.gramaticas import Gramatica
from src.ll.tabela_ll1 import TabelaLL1


class ParserLL1:
    def __init__(self, tabela: TabelaLL1, gramatica: Gramatica) -> None:
        self.tabela = tabela
        self.gramatica = gramatica
        self.derivacao: List[str] = []

    