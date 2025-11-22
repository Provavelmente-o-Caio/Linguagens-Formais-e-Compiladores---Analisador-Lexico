"""Classes para representação de gramáticas livres de contexto.

Este módulo define as estruturas fundamentais para trabalhar com gramáticas:
símbolos (terminais e não-terminais) e produções.

Referência: Aho et al., Capítulo 4 "Análise Sintática".
"""

from dataclasses import dataclass
from typing import List, Union
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


@dataclass
class Producao:
    """Representa uma produção da gramática livre de contexto.
    
    Formato: A ::= α, onde A é não-terminal e α é sequência de símbolos.
    
    Attributes:
        cabeca: Não-terminal do lado esquerdo da produção.
        corpo: Lista de símbolos do lado direito da produção.
        numero: Número identificador único da produção.
    """
    cabeca: NaoTerminal
    corpo: List[Union[Terminal, NaoTerminal]]
    numero: int
    
    def __repr__(self) -> str:
        corpo_str = " ".join(str(s) for s in self.corpo) if self.corpo else "ε"
        return f"{self.cabeca} ::= {corpo_str}"
