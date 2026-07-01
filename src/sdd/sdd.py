from src.sdd.dec_tree import NodeDec


class SDD:
    def __init__(self, escopo):
        self.escopo = escopo
        self.declaracoes_processadas = 0

    def aplicar(self, tokens: list[tuple[str, str]]):
        self.declaracoes_processadas = 0
        self.aplicar_declaracoes(tokens)
        print(f"SDD: {self.declaracoes_processadas} declaração(ões) processada(s).")

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
        print(f"SDD: {nome} tipado como {tipo_declarado}")

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

    def _eh_tipo_de_alloc(self, tokens: list[tuple[str, str]], posicao: int) -> bool:
        if posicao == 0:
            return False

        lexema_anterior, _ = tokens[posicao - 1]
        return lexema_anterior == "new"

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
