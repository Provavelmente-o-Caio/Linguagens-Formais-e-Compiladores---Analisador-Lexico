from typing import Dict, List, Set, Tuple

from src.gramaticas import Epsilon, HandlerGramatica, NaoTerminal, Producao, Terminal
from src.ll.acoes import ConflictErrorLL1

_EPSILON = Epsilon()


class TabelaLL1:
    def __init__(self):
        self.tabela: Dict[Tuple[NaoTerminal, Terminal], Producao] = {}

    @staticmethod
    def _first_sequencia(simbolos: Tuple, handler: HandlerGramatica) -> Set[Terminal]:
        resultado: Set[Terminal] = set()

        if not simbolos:
            return {_EPSILON}

        for simbolo in simbolos:
            first_xi: Set[Terminal] = handler.get_first(simbolo)
            resultado |= first_xi - {_EPSILON}
            if _EPSILON not in first_xi:
                return resultado  # este símbolo bloqueia ε

        resultado.add(_EPSILON)  # toda a sequência deriva ε
        return resultado

    def construir(self, producoes: List[Producao], handler: HandlerGramatica) -> None:
        for producao in producoes:
            cabeca = producao.cabeca
            corpo = producao.corpo

            tem_epsilon = False
            for simbolo in self._first_sequencia(corpo, handler):
                if isinstance(simbolo, Terminal) and simbolo == _EPSILON:
                    tem_epsilon = True
                    continue
                self._inserir(cabeca, simbolo, producao)

            if tem_epsilon:
                for terminal in handler.get_follow(cabeca):
                    self._inserir(cabeca, terminal, producao)

    def _inserir(
        self, nao_terminal: NaoTerminal, terminal: Terminal, producao: Producao
    ) -> None:
        chave: Tuple[NaoTerminal, Terminal] = (nao_terminal, terminal)

        # conflito -> outro símbolo já presente
        if self.tabela.get(chave) and self.tabela.get(chave) != producao:
            print(f"[AVISO] {ConflictErrorLL1(chave, self.tabela[chave], producao)}")
            return

        self.tabela[chave] = producao

    def consultar(
        self, nao_terminal: NaoTerminal, terminal: Terminal
    ) -> Producao | None:
        return self.tabela.get((nao_terminal, terminal))
