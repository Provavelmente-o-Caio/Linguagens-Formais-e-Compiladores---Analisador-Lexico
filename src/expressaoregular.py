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
            # Epsilon não mostra posição (pos = -1)
            if self.valor == EPSILON:
                return EPSILON
            return f"{self.valor}({self.pos})"
        elif self.tipo == "*":
            return f"({self.nodo_esquerda})*"
        elif self.tipo == "|":
            return f"({self.nodo_esquerda}|{self.nodo_direita})"
        elif self.tipo == ".":
            return f"({self.nodo_esquerda}.{self.nodo_direita})"
        else:
            return self.tipo


class ExpressaoRegular:
    def __init__(self, expressao: str) -> None:
        # Adiciona concatenação explícita com # para marcar fim da expressão
        self.expressao: list[str] = list(f"({self.formatar_expressao(expressao)}).#")
        self.posicao: int = 1

    def formatar_expressao(self, expressao: str) -> str:
        """Insere concatenação explícita (.)"""
        resultado: list[str] = []
        anterior: str | None = None

        for atual in expressao:
            if anterior:
                if (anterior.isalnum() or anterior in [")", "*", "+", "?"]) and (
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
            nodo_direita = self.parse_concatenacao()
            nodo = NodoER(token, nodo_esquerda=nodo, nodo_direita=nodo_direita)

        # Verifica se ainda há tokens não consumidos (exceto quando tudo foi parseado corretamente)
        if self.olhar() is not None and self.olhar() not in [")", None]:
            raise ValueError(f"Caractere inesperado após parse: {self.olhar()}")

        return nodo

    def parse_concatenacao(self) -> NodoER:
        nodo = self.parse_kleene()
        while self.olhar() == ".":
            token = self.consume(".")
            nodo = NodoER(token, nodo_esquerda=nodo, nodo_direita=self.parse_kleene())
        return nodo

    def parse_kleene(self) -> NodoER:
        nodo = self.parse_atomico()
        while self.olhar() in ["*", "?", "+"]:
            token = self.consume(self.olhar())
            if token == "*":
                nodo = NodoER("*", nodo_esquerda=nodo)
            elif token == "?":
                # a? => (a|ε)
                # Cria nodo epsilon com posição -1 (não é folha real)
                nodo_epsilon = NodoER("SIMBOLO", EPSILON, -1)
                # Cria união
                nodo = NodoER("|", nodo_esquerda=nodo, nodo_direita=nodo_epsilon)
            elif token == "+":
                # a+ => a.a*
                nodo_copia = self.copiar_subarvore(nodo)
                nodo = NodoER(
                    ".",
                    nodo_esquerda=nodo,
                    nodo_direita=NodoER("*", nodo_esquerda=nodo_copia),
                )

        return nodo

    def parse_atomico(self) -> NodoER:
        atual = self.olhar()

        if atual in ["*", "+", "?", "|", ")"]:
            raise ValueError(f"Operador '{atual}' sem operando à esquerda")

        if atual == "(":
            _ = self.consume("(")
            nodo = self.parse()
            if self.olhar() != ")":
                raise ValueError(f"Esperado ')', obtido: {self.olhar()}")
            _ = self.consume(")")
            return nodo

        # Qualquer outro símbolo (incluindo '#' de fim) é tratado como SIMBOLO
        # O '#' é adicionado automaticamente no __init__ e recebe uma posição
        token = self.consume(None)
        nodo = NodoER("SIMBOLO", token, self.posicao)
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

    def copiar_subarvore(self, nodo: NodoER) -> NodoER:
        """Cria cópia profunda de uma subárvore, atribuindo novas posições aos símbolos"""
        if nodo.tipo == "SIMBOLO":
            # Epsilon mantém posição -1, outros símbolos recebem nova posição
            if nodo.valor == EPSILON:
                return NodoER("SIMBOLO", EPSILON, -1)
            novo = NodoER("SIMBOLO", nodo.valor, self.posicao)
            self.posicao += 1
            return novo

        # Para operadores, copia recursivamente
        esquerda: NodoER | None = (
            self.copiar_subarvore(nodo.nodo_esquerda) if nodo.nodo_esquerda else None
        )
        direita: NodoER | None = (
            self.copiar_subarvore(nodo.nodo_direita) if nodo.nodo_direita else None
        )

        return NodoER(
            nodo.tipo, nodo.valor, nodo_esquerda=esquerda, nodo_direita=direita
        )
