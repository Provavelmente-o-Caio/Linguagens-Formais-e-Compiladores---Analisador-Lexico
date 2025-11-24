from __future__ import annotations

from dataclasses import dataclass, field
from typing import override

EPSILON = "&"
MAPA_OPERADORES = {
    ">=": "≥",
    "<=": "≤",
    "==": "≡",
    "<>": "≠",
    "!=": "≠",
    ":=": "←",
}
OPERADORES_UNITARIOS = {
    "+": "⊕",
    "-": "−",
    "*": "×",
    "/": "÷",
    "(": "⟮",
    ")": "⟯",
    ".": "•",
}


@dataclass
class NodoER:
    """Nodo da árvore de uma expressão regular.

    Representa um nodo interno (operador) ou folha (símbolo) da árvore da ER.
    Armazena informações para construção direta de AFD (análise léxica).

    Referência: Aho et al., Seção 3.9 "De uma Expressão Regular para um AFD".

    Attributes:
        tipo: Tipo do nodo ("SIMBOLO", "|", ".", "*").
        valor: Símbolo para folhas, None para operadores.
        pos: Posição única da folha na expressão.
        nullable: True se o nodo pode gerar string vazia.
        firstpos: Conjunto de posições que podem iniciar strings geradas.
        lastpos: Conjunto de posições que podem finalizar strings geradas.
        followpos: Conjunto de posições que podem seguir esta posição.
        nodo_esquerda: Subárvore esquerda (para operadores binários e unários).
        nodo_direita: Subárvore direita (para operadores binários).
    """

    # valor nodo
    tipo: str  # simbolo, *, ?, |, (, ), .
    valor: str | None = None

    # para a árvore
    pos: int = 0
    nullable: bool = True
    firstpos: set[int] = field(default_factory=set)
    followpos: set[int] = field(default_factory=set)
    lastpos: set[int] = field(default_factory=set)

    # ligações
    nodo_esquerda: NodoER | None = None
    nodo_direita: NodoER | None = None

    def calcula_posicoes(self) -> None:
        """
        Calcula nullable, firstpos e lastpos para um nodo da árvore da ER.

        As regras são:
        - Para folha (símbolo): nullable = false (exceto ε), firstpos = lastpos = {pos}
        - Para união (|): nullable = c1.nullable OU c2.nullable
        - Para concatenação (.): nullable = c1.nullable E c2.nullable
        - Para fecho (*): nullable = true
        """
        if self.tipo == "SIMBOLO":
            if self.valor == EPSILON:
                self.nullable = True
                self.firstpos = set()
                self.lastpos = set()
            else:
                self.nullable = False
                self.firstpos = {self.pos}
                self.lastpos = {self.pos}
        elif self.tipo == "|":
            if self.nodo_esquerda and self.nodo_direita:
                self.nullable = (
                    self.nodo_esquerda.nullable or self.nodo_direita.nullable
                )
                self.firstpos = self.nodo_esquerda.firstpos.union(
                    self.nodo_direita.firstpos
                )
                self.lastpos = self.nodo_esquerda.lastpos.union(
                    self.nodo_direita.lastpos
                )
            else:
                raise ValueError(
                    "Os ramos de uma união não estão completamente preenchidos"
                )
        elif self.tipo == ".":
            if self.nodo_esquerda and self.nodo_direita:
                self.nullable = (
                    self.nodo_esquerda.nullable and self.nodo_direita.nullable
                )
                if self.nodo_esquerda.nullable:
                    self.firstpos = self.nodo_esquerda.firstpos.union(
                        self.nodo_direita.firstpos
                    )
                else:
                    self.firstpos = self.nodo_esquerda.firstpos

                if self.nodo_direita.nullable:
                    self.lastpos = self.nodo_direita.lastpos.union(
                        self.nodo_esquerda.lastpos
                    )
                else:
                    self.lastpos = self.nodo_direita.lastpos
            else:
                raise ValueError(
                    "Os ramos de uma concatenação não estão completamente preenchidos"
                )
        elif self.tipo == "*":
            if self.nodo_esquerda:
                self.nullable = True
                self.firstpos = self.nodo_esquerda.firstpos
                self.lastpos = self.nodo_esquerda.lastpos
            else:
                raise ValueError(
                    "Os ramos de um fecho não estão completamente preenchidos"
                )

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
    """Processador de expressões regulares para construção direta de AFD.

    Implementa análise de ERs com parser descendente recursivo e cálculo de funções
    auxiliares (nullable, firstpos, lastpos, followpos) para construção
    direta de AFD (analisador léxico) sem passar por AFND.

    Referência: Aho et al., Seção 3.9 "De Expressões Regulares para Autômatos".
    """

    def __init__(self, expressao: str) -> None:
        """Inicializa processador de ER.

        Adiciona concatenação explícita e marcador de fim (#) automaticamente.

        Args:
            expressao: String contendo a expressão regular.
        """
        # Adiciona concatenação explícita com # para marcar fim da expressão
        expressao = substituir_operadores_multicaracteres(expressao)
        self.expressao: list[str] = list(f"({self.formatar_expressao(expressao)}).#")
        self.posicao: int = 1
        self.folhas: dict[int, NodoER] = {}

    def formatar_expressao(self, expressao: str) -> str:
        """
        Insere concatenação explícita (.) onde necessário.

        A concatenação explícita facilita o parsing e construção da árvore da ER.
        """
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
        """
        Parser descendente recursivo para expressões regulares.

        Analisa a estrutura da ER seguindo precedência de operadores:
        E → C ('|' C)*        (união - menor precedência)
        C → K ('.' K)*        (concatenação)
        K → A ('*'|'+'|'?')*  (operadores unários)
        A → símbolo | '(' E ')'  (átomos - maior precedência)
        """
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
        """Parseia concatenação de expressões.

        Estrutura: C → K ('.' K)*

        Returns:
            Nodo representando concatenação de subexpressões.
        """
        nodo = self.parse_kleene()
        while self.olhar() == ".":
            token = self.consume(".")
            nodo = NodoER(token, nodo_esquerda=nodo, nodo_direita=self.parse_kleene())
        return nodo

    def parse_kleene(self) -> NodoER:
        """Parseia operadores de Kleene (*, +, ?).

        Estrutura: K → A ('*'|'+'|'?')*
        Expansões:
        - a* → fecho de Kleene
        - a+ → a.a* (uma ou mais ocorrências)
        - a? → (a|ε) (opcional)

        Returns:
            Nodo representando expressão com operadores de Kleene aplicados.
        """
        nodo = self.parse_atomico()
        while self.olhar() in ["*", "?", "+"]:
            token = self.consume(self.olhar())
            if token == "*":
                nodo = NodoER("*", nodo_esquerda=nodo)
            elif token == "?":
                # a? => (a|ε)
                # Cria nodo epsilon com posição -1 (não é folha real)
                nodo_epsilon = NodoER("SIMBOLO", EPSILON, 0)
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
        """Parseia expressões atômicas (símbolos ou subexpressões entre parênteses).

        Estrutura: A → símbolo | '(' E ')'

        Returns:
            Nodo representando símbolo individual ou subexpressão.

        Raises:
            ValueError: Se encontrar operador sem operando ou parênteses desbalanceados.
        """
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
        token: str = self.consume(None)
        nodo: NodoER = NodoER("SIMBOLO", token, self.posicao)
        self.folhas[self.posicao] = nodo
        self.posicao += 1
        print("token: ", token)
        return nodo

    def consume(self, esperado: str | None) -> str:
        """Consome próximo token da entrada.

        Args:
            esperado: Token esperado ou None para aceitar qualquer token.

        Returns:
            Token consumido.

        Raises:
            ValueError: Se token não corresponder ao esperado ou entrada estiver vazia.
        """
        if not self.expressao:
            raise ValueError("Erro de expressão era esperado")
        ch: str = self.expressao.pop(0)
        if esperado and esperado != ch:
            raise ValueError(
                f"Valor diferente do esperado {esperado}, o valor obtido foi: {ch}"
            )
        return ch

    def olhar(self) -> str | None:
        """Retorna próximo token sem consumi-lo (lookahead).

        Returns:
            Próximo token ou None se entrada vazia.
        """
        return self.expressao[0] if self.expressao else None

    def copiar_subarvore(self, nodo: NodoER) -> NodoER:
        """Cria cópia profunda de uma subárvore com novas posições.

        Necessário para expansão de operadores como a+ → a.a*, onde o símbolo
        'a' aparece duas vezes e precisa de posições distintas.

        Args:
            nodo: Raiz da subárvore a ser copiada.

        Returns:
            Nova subárvore com mesma estrutura mas novas posições para símbolos.
        """
        if nodo.tipo == "SIMBOLO":
            # Epsilon mantém posição -1, outros símbolos recebem nova posição
            if nodo.valor == EPSILON:
                return NodoER("SIMBOLO", EPSILON, -1)
            novo: NodoER = NodoER("SIMBOLO", nodo.valor, self.posicao)
            self.folhas[self.posicao] = novo
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

    def calcular_followpos(self, raiz: NodoER | None) -> None:
        """
        Calcula o conjunto followpos de todos os nodos da árvore.

        Regras:
        - Para concatenação (n = c1.c2): para cada i em lastpos(c1), followpos(i) contém firstpos(c2)
        - Para fecho (n = c1*): para cada i em lastpos(n), followpos(i) contém firstpos(n)
        """
        if raiz is None:
            return

        self.calcular_followpos(raiz.nodo_esquerda)
        self.calcular_followpos(raiz.nodo_direita)

        if raiz.tipo == ".":
            if raiz.nodo_esquerda and raiz.nodo_direita:
                for i in raiz.nodo_esquerda.lastpos:
                    self.folhas[i].followpos.update(raiz.nodo_direita.firstpos)
        elif raiz.tipo == "*":
            for i in raiz.lastpos:
                self.folhas[i].followpos.update(raiz.firstpos)

    def visitar(self, n: NodoER | None):
        """
        Calcula as posições de um nodo e de seus nodos abaixo recursivamente.

        Percorre a árvore em pós-ordem para calcular nullable, firstpos, lastpos.
        """
        if n is None:
            return
        else:
            self.visitar(n.nodo_esquerda)
            self.visitar(n.nodo_direita)
            n.calcula_posicoes()

    def processar(self) -> NodoER:
        """
        Processa a expressão regular e retorna a raiz da árvore construída.

        Passos:
        1. Constrói árvore da ER aumentada (adiciona # no final)
        2. Calcula nullable, firstpos, lastpos para cada nodo
        3. Calcula followpos para cada posição
        """
        raiz = self.parse()

        self.visitar(raiz)
        self.calcular_followpos(raiz)

        return raiz


def substituir_operadores_multicaracteres(expressao: str):
    # substitui multi-caracter
    for op in sorted(MAPA_OPERADORES, key=len, reverse=True):
        expressao = expressao.replace(op, MAPA_OPERADORES[op])

    # substitui unitários APENAS se expressão for exatamente o operador
    if expressao in OPERADORES_UNITARIOS:
        return OPERADORES_UNITARIOS[expressao]

    return expressao
