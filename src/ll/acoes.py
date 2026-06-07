from dataclasses import dataclass

from src.gramaticas import NaoTerminal, Producao, Terminal


@dataclass
class ConflictErrorLL1(Exception):
    def __init__(
        self,
        chave: tuple[NaoTerminal, Terminal],
        producao_antiga: Producao,
        producao_nova: Producao,
    ):
        mensagem = f"CONFLITO em {chave}: {producao_antiga} vs {producao_nova}"
        super().__init__(mensagem)
