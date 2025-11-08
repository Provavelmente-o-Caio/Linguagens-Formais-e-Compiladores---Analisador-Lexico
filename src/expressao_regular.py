from __future__ import annotations
from dataclasses import dataclass
from typing import override

EPSILON = "ε"


@dataclass
class NodoER:
    # valor nodo
    tipo: str  # simbolo, *, ?, |, (, ), .
    valor: str | None = None

    # para a árvore
    pos: int = 0
    nullable: bool = False
    firstpos: set[NodoER] = set()
    followpos: set[NodoER] = set()
    lastpos: set[NodoER] = set()

    # ligações
    nodo_esquerda: NodoER | None = None
    nodo_direita: NodoER | None = None

    @override
    def __repr__(self) -> str:
        if self.tipo == "SIMBOLO":
            return f"{self.valor or EPSILON}({self.pos})"
        elif self.tipo == "*":
            return f"({self.nodo_esquerda})*"
        elif self.tipo == "|":
            return f"({self.nodo_esquerda}|{self.nodo_direita})"
        elif self.tipo == ".":
            return f"({self.nodo_esquerda}.{self.nodo_direita})"
        elif self.tipo == "?":
            return f"({self.nodo_esquerda}|{EPSILON})"
        else:
            return self.tipo


class Expressao_Regular:
    def __init__(self, expressao: str) -> None:
        self.expressao: list[str] = list(f"({expressao})#")
        self.posicao: int = 1

    def parse(self) -> NodoER:
        pass

    def parse_concatenacao(self) -> NodoER:
        nodo = self.parse_kleene()
        while

    def parse_kleene(self) -> NodoER:
        nodo: NodoER = self.parse_atomico()
        while self.olhar() == "*":
            token = self.consume("*")
            nodo = NodoER(token, nodo_esquerda=nodo)
        return nodo

    def parse_atomico(self) -> NodoER:
        if self.olhar == "(":
            token = self.consume("(")
            nodo = self.parse()
            token = self.consume(")")
            return nodo
        else:
            token = self.consume(None)
            nodo: NodoER = NodoER("SIMBOLO", token, self.posicao)
            self.posicao += 1
            return nodo


    def consume(self, esperado: str | None) -> str:
        if self.expressao:
            raise ValueError("Erro de expressão era esperado")
        ch: str = self.expressao.pop(0)
        if esperado and esperado != ch:
            raise ValueError(
                f"Valor diferente do esperado {esperado}, o valor obtido foi: {ch}"
            )
        return ch

    def olhar(self) -> str | None:
        return self.expressao[0] if self.expressao else None
