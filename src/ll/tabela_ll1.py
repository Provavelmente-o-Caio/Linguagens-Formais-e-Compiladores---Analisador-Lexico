from typing import Dict, List, Tuple

from src.gramaticas import (
    HandlerGramatica,
    NaoTerminal,
    Producao,
    Terminal,
)
from src.ll.acoes import ConflictErrorLL1


class TabelaLL1:
    def __init__(self):
        self.tabela: Dict[Tuple[NaoTerminal, Terminal], Producao] = {}

    def construir(self, producoes: List[Producao], handler: HandlerGramatica) -> None:
        fim_entrada = Terminal("$")

        for producao in producoes:
            cabeca = producao.cabeca
            corpo = producao.corpo

            tem_epsilon = False
            for simbolo in handler.get_first(corpo):
                if isinstance(simbolo, Terminal) and simbolo.nome == "ε":
                    tem_epsilon = True
                    continue
                if isinstance(simbolo, Terminal):
                    self._inserir(cabeca, simbolo, producao)

            if tem_epsilon or not corpo:
                for terminal in handler.get_follow(cabeca):
                    self._inserir(cabeca, terminal, producao)

    def _inserir(
        self, nao_terminal: NaoTerminal, terminal: Terminal, producao: Producao
    ) -> None:
        chave: Tuple[NaoTerminal, Terminal] = (nao_terminal, terminal)

        # conflito -> outro símbolo já presente
        if self.tabela.get(chave) and self.tabela.get(chave) != producao:
            raise ConflictErrorLL1(chave, self.tabela[chave], producao)
        else:
            self.tabela[chave] = producao

    def consultar(
        self, nao_terminal: NaoTerminal, terminal: Terminal
    ) -> Producao | None:
        return self.tabela.get((nao_terminal, terminal))
