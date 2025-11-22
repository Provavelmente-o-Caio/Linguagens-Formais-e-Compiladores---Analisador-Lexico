from dataclasses import dataclass
from typing import Union
from .simbolos import Terminal, NaoTerminal


@dataclass(frozen=True)
class Producao:
    """Representa uma produção da gramática livre de contexto.
    
    Formato: A ::= α, onde A é não-terminal e α é sequência de símbolos.
    
    Attributes:
        cabeca: Não-terminal do lado esquerdo da produção.
        corpo: Tupla de símbolos do lado direito da produção.
        numero: Número identificador único da produção.
    """
    cabeca: NaoTerminal
    corpo: tuple[Union[Terminal, NaoTerminal], ...]
    numero: int
    
    def __repr__(self) -> str:
        corpo_str = " ".join(str(s) for s in self.corpo) if self.corpo else "ε"
        return f"{self.cabeca} ::= {corpo_str}"
