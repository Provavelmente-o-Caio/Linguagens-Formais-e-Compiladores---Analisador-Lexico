"""Ações do parser SLR.

Referência: Dragon Book, Seção 4.7 "Analisadores Sintáticos LR".
"""

from dataclasses import dataclass
from typing import Union


@dataclass(frozen=True)
class Shift:
    """Ação shift: empilha estado e avança para próximo símbolo.
    
    ACTION[i, a] = shift j
    """
    estado: int
    
    def __str__(self) -> str:
        return f"s{self.estado}"


@dataclass(frozen=True)
class Reduce:
    """Ação reduce: reduz usando uma produção da gramática.
    
    ACTION[i, a] = reduce A::=β
    """
    producao: int  # Número da produção
    
    def __str__(self) -> str:
        return f"r{self.producao}"


@dataclass(frozen=True)
class Accept:
    """Ação accept: aceita a entrada.
    
    ACTION[i, $] = accept
    """
    
    def __str__(self) -> str:
        return "acc"


# Tipo união para todas as ações possíveis
Acao = Union[Shift, Reduce, Accept]


class ConflitoError(Exception):
    """Exceção lançada quando há conflito shift-reduce ou reduce-reduce na tabela SLR.
    
    Referência: Dragon Book, Seção 4.7 - Gramáticas que não são SLR podem ter conflitos.
    """
    def __init__(self, estado: int, simbolo, acao_anterior: str, nova_acao: str):
        self.estado = estado
        self.simbolo = simbolo
        self.acao_anterior = acao_anterior
        self.nova_acao = nova_acao
        mensagem = f"CONFLITO em ACTION[{estado}, {simbolo}]: {acao_anterior} vs {nova_acao}"
        super().__init__(mensagem)
