from __future__ import annotations
from dataclasses import dataclass, field
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
    firstpos: set[NodoER] = field(default_factory=set)
    followpos: set[NodoER] = field(default_factory=set)
    lastpos: set[NodoER] = field(default_factory=set)

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


class ExpressaoRegular:
    def __init__(self, expressao: str) -> None:
        self.expressao: list[str] = list(f"({self.formatar_expressao(expressao)})#")
        self.posicao: int = 1

    def formatar_expressao(self, expressao: str) -> str:
        resultado: list[str] = []
        anterior: str | None = None

        for atual in expressao:
            if anterior:
                if (anterior.isalnum() or anterior in [")", "*", "?"]) and (
                    atual.isalnum() or atual == "("
                ):
                    resultado.append(".")
            resultado.append(atual)
            anterior = atual

        return "".join(resultado)

    def parse(self) -> NodoER:
        nodo: NodoER = self.parse_concatenacao()
        while self.olhar() == "|":
            token = self.consume("|")
            nodo = NodoER(
                token, nodo_esquerda=nodo, nodo_direita=self.parse_concatenacao()
            )
        return nodo

    def parse_concatenacao(self) -> NodoER:
        nodo = self.parse_kleene()
        while self.olhar() == ".":
            token = self.consume(".")
            nodo = NodoER(token, nodo_esquerda=nodo, nodo_direita=self.parse_kleene())
        return nodo

    def parse_kleene(self) -> NodoER:
        nodo: NodoER = self.parse_atomico()
        while self.olhar() in ["*", "?", "+"]:
            if self.olhar() == "+":
                # a+a = a.a*
                token = self.consume("+")
                nodo = NodoER(
                    ".",
                    nodo_esquerda=nodo,
                    nodo_direita=NodoER("*", nodo_esquerda=nodo),
                )
            else:
                token = self.consume(self.olhar())
                nodo = NodoER(token, nodo_esquerda=nodo)
        return nodo

    def parse_atomico(self) -> NodoER:
        if self.olhar() == "(":
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
        if not self.expressao:
            raise ValueError("Erro de expressão era esperado")
        ch: str = self.expressao.pop(0)
        if esperado and esperado != ch:
            raise ValueError(
                f"Valor diferente do esperado {esperado}, o valor obtido foi: {ch}"
            )
        return ch

    def olhar(self) -> str | None:
        return self.expressao[0] if self.expressao else None
