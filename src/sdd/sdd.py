from src.sdd.dec_tree import NodeDec


class SDD:
    def __init__(self, escopo):
        self.escopo = escopo
        self.declaracoes_processadas = 0
        self.declaracoes = []
        self.erros = []

    def aplicar(self, tokens: list[tuple[str, str]]):
        self.declaracoes_processadas = 0
        self.declaracoes = []
        self.erros = []

        self.aplicar_declaracoes(tokens)
        self.verificar_tipos_expressoes(tokens)

    def aplicar_declaracoes(self, tokens: list[tuple[str, str]]):
        tipos_validos = {"int", "float", "string"}
        i = 0

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema not in tipos_validos:
                i += 1
                continue

            if self._eh_tipo_de_alloc(tokens, i):
                i += 1
                continue

            tipo = lexema
            j = i + 1

            if j < len(tokens):
                nome, categoria = tokens[j]

                if self._eh_identificador(nome, categoria):
                    self._registrar_declaracao(nome, tipo)

                    i = self._avancar_ate_fim_declaracao(tokens, j + 1)
                    continue

            i += 1

    def _registrar_declaracao(self, nome: str, tipo: str):
        arvore = NodeDec(
            "VARDECL",
            children=[
                NodeDec(
                    "TYPE",
                    children=[
                        NodeDec.leaf(tipo),
                    ],
                ),
                NodeDec.leaf(nome),
            ],
        )

        arvore.proc_tree()
        tipo_declarado = arvore.type

        if tipo_declarado is None:
            return

        entrada = self.escopo.tabela.obter(nome)

        if entrada is None:
            entrada = self.escopo.tabela.lookup(nome)

        entrada.tipo = tipo_declarado
        entrada.escopo = self.escopo.numero

        self.declaracoes_processadas += 1
        self.declaracoes.append((nome, tipo_declarado, self.escopo.numero))

    def verificar_tipos_expressoes(self, tokens: list[tuple[str, str]]):
        i = 0

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema == "=":
                inicio = i + 1
                fim = self._encontrar_fim_expressao(tokens, inicio)

                if inicio < fim and not self._eh_alloc_expressao(tokens, inicio):
                    self._verificar_expressao(tokens[inicio:fim])

                i = fim
                continue

            if lexema == "print":
                inicio = i + 1
                fim = self._encontrar_fim_expressao(tokens, inicio)

                if inicio < fim:
                    self._verificar_expressao(tokens[inicio:fim])

                i = fim
                continue

            if lexema == "return":
                inicio = i + 1
                fim = self._encontrar_fim_expressao(tokens, inicio)

                if inicio < fim:
                    self._verificar_expressao(tokens[inicio:fim])

                i = fim
                continue

            if lexema == "if":
                inicio = self._proximo_token(tokens, i, "(")
                fim = self._fechar_parenteses(tokens, inicio)

                if inicio is not None and fim is not None:
                    self._verificar_expressao(tokens[inicio + 1:fim])
                    i = fim + 1
                    continue

            if lexema == "for":
                i = self._verificar_for(tokens, i)
                continue

            i += 1

    def _verificar_for(self, tokens: list[tuple[str, str]], posicao_for: int) -> int:
        abre = self._proximo_token(tokens, posicao_for, "(")

        if abre is None:
            return posicao_for + 1

        fecha = self._fechar_parenteses(tokens, abre)

        if fecha is None:
            return posicao_for + 1

        partes = self._separar_por_ponto_virgula(tokens[abre + 1:fecha])

        for parte in partes:
            if not parte:
                continue

            for indice, (lexema, _) in enumerate(parte):
                if lexema == "=":
                    expr = parte[indice + 1:]
                    if expr and not self._eh_alloc_expressao(expr, 0):
                        self._verificar_expressao(expr)
                    break
            else:
                self._verificar_expressao(parte)

        return fecha + 1

    def _verificar_expressao(self, expressao: list[tuple[str, str]]):
        operadores_aritmeticos = {"+", "-", "*", "/", "%"}
        operadores_relacionais = {"<", ">", "<=", ">=", "==", "!="}

        possui_operador = any(
            lexema in operadores_aritmeticos or lexema in operadores_relacionais
            for lexema, _ in expressao
        )

        if not possui_operador:
            return

        tipos_encontrados = []

        i = 0
        while i < len(expressao):
            lexema, categoria = expressao[i]

            if self._eh_chamada_funcao(expressao, i):
                i = self._pular_chamada_funcao(expressao, i)
                continue

            tipo = self._tipo_operando(lexema, categoria)

            if tipo is not None:
                tipos_encontrados.append((lexema, tipo))

            i += 1

        tipos_distintos = {tipo for _, tipo in tipos_encontrados}

        if len(tipos_distintos) > 1:
            expr_texto = " ".join(lexema for lexema, _ in expressao)
            detalhes = ", ".join(
                f"{lexema}:{tipo}" for lexema, tipo in tipos_encontrados
            )
            self.erros.append(
                f"Erro semântico: expressão '{expr_texto}' possui operandos "
                f"com tipos incompatíveis ({detalhes})."
            )

    def _tipo_operando(self, lexema: str, categoria: str) -> str | None:
        if categoria == "intconstant":
            return "int"

        if categoria == "floatconstant":
            return "float"

        if categoria == "stringconstant":
            return "string"

        if lexema == "null":
            return "null"

        if categoria.lower() == "id":
            entrada = self.escopo.encontrar_simbolo(lexema)

            if entrada is None:
                self.erros.append(
                    f"Erro semântico: identificador '{lexema}' não declarado."
                )
                return None

            if entrada.tipo is None:
                return None

            return entrada.tipo

        return None

    def _encontrar_fim_expressao(
        self,
        tokens: list[tuple[str, str]],
        inicio: int,
    ) -> int:
        profundidade_parenteses = 0
        profundidade_colchetes = 0
        i = inicio

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema == "(":
                profundidade_parenteses += 1
            elif lexema == ")" and profundidade_parenteses > 0:
                profundidade_parenteses -= 1
            elif lexema == "[":
                profundidade_colchetes += 1
            elif lexema == "]" and profundidade_colchetes > 0:
                profundidade_colchetes -= 1
            elif (
                lexema in {";", "{", "}"}
                and profundidade_parenteses == 0
                and profundidade_colchetes == 0
            ):
                return i
            elif (
                lexema == ","
                and profundidade_parenteses == 0
                and profundidade_colchetes == 0
            ):
                return i

            i += 1

        return i

    def _eh_alloc_expressao(
        self,
        tokens: list[tuple[str, str]],
        inicio: int,
    ) -> bool:
        return inicio < len(tokens) and tokens[inicio][0] == "new"

    def _eh_tipo_de_alloc(self, tokens: list[tuple[str, str]], posicao: int) -> bool:
        if posicao == 0:
            return False

        lexema_anterior, _ = tokens[posicao - 1]
        return lexema_anterior == "new"

    def _eh_identificador(self, lexema: str, categoria: str) -> bool:
        if categoria.lower() == "id":
            return True

        if categoria.isdigit():
            return True

        palavras_reservadas = {
            "def",
            "if",
            "else",
            "for",
            "break",
            "return",
            "print",
            "read",
            "new",
            "int",
            "float",
            "string",
            "null",
        }

        return lexema not in palavras_reservadas

    def _eh_chamada_funcao(
        self,
        tokens: list[tuple[str, str]],
        posicao: int,
    ) -> bool:
        if posicao + 1 >= len(tokens):
            return False

        lexema, categoria = tokens[posicao]
        proximo, _ = tokens[posicao + 1]

        return categoria.lower() == "id" and proximo == "("

    def _pular_chamada_funcao(
        self,
        tokens: list[tuple[str, str]],
        posicao: int,
    ) -> int:
        abre = posicao + 1
        fecha = self._fechar_parenteses(tokens, abre)

        if fecha is None:
            return posicao + 1

        return fecha + 1

    def _proximo_token(
        self,
        tokens: list[tuple[str, str]],
        inicio: int,
        esperado: str,
    ) -> int | None:
        i = inicio

        while i < len(tokens):
            if tokens[i][0] == esperado:
                return i
            i += 1

        return None

    def _fechar_parenteses(
        self,
        tokens: list[tuple[str, str]],
        abre: int,
    ) -> int | None:
        profundidade = 0
        i = abre

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema == "(":
                profundidade += 1
            elif lexema == ")":
                profundidade -= 1

                if profundidade == 0:
                    return i

            i += 1

        return None

    def _separar_por_ponto_virgula(
        self,
        tokens: list[tuple[str, str]],
    ) -> list[list[tuple[str, str]]]:
        partes = []
        atual = []
        profundidade_parenteses = 0
        profundidade_colchetes = 0

        for token in tokens:
            lexema, _ = token

            if lexema == "(":
                profundidade_parenteses += 1
            elif lexema == ")" and profundidade_parenteses > 0:
                profundidade_parenteses -= 1
            elif lexema == "[":
                profundidade_colchetes += 1
            elif lexema == "]" and profundidade_colchetes > 0:
                profundidade_colchetes -= 1

            if (
                lexema == ";"
                and profundidade_parenteses == 0
                and profundidade_colchetes == 0
            ):
                partes.append(atual)
                atual = []
            else:
                atual.append(token)

        if atual:
            partes.append(atual)

        return partes

    def _avancar_ate_fim_declaracao(
        self,
        tokens: list[tuple[str, str]],
        inicio: int,
    ) -> int:
        profundidade_colchetes = 0
        i = inicio

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema == "[":
                profundidade_colchetes += 1
            elif lexema == "]" and profundidade_colchetes > 0:
                profundidade_colchetes -= 1
            elif lexema in {",", ")", ";"} and profundidade_colchetes == 0:
                return i + 1
            elif lexema in {
                "def",
                "if",
                "for",
                "return",
                "print",
                "read",
                "break",
                "{",
                "}",
            }:
                return i

            i += 1

        return i
