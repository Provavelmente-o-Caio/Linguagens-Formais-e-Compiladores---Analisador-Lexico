from dataclasses import dataclass
from abc import ABC


EPSILON = "&"


@dataclass(frozen=True)
class Simbolo(ABC):
    """Classe base para símbolos da gramática.
    
    Attributes:
        nome: Nome do símbolo.
    """
    nome: str
    
    def __repr__(self) -> str:
        return f"{self.nome}"


@dataclass(frozen=True, repr=False)
class Terminal(Simbolo):
    """Representa um símbolo terminal da gramática.
    
    Terminais são símbolos que aparecem na entrada (tokens).
    Exemplos: +, *, (, ), id, num, if, while
    """
    pass


@dataclass(frozen=True, repr=False)
class NaoTerminal(Simbolo):
    """Representa um símbolo não-terminal da gramática.
    
    Não-terminais são variáveis sintáticas que podem ser expandidas.
    Exemplos: <E>, <T>, <F>, <expr>, <stmt>
    """
    pass


@dataclass(frozen=True, repr=False)
class Epsilon(Terminal):
    """Representa o símbolo especial epsilon (produção vazia)."""
    
    def __init__(self):
        super().__init__(EPSILON)

    def __repr__(self) -> str:
        return "ε"
