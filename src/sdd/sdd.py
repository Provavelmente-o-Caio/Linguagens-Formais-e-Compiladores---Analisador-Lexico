from src.sdd.dec_tree import NodeDec

class SDD:
    def __init__(self, escopo):
        self.escopo = escopo

    def aplicar(self, tokens):
        self.aplicar_declaracoes(tokens)

    def aplicar_declaracoes(self, tokens):
        tipos_validos = {"int", "float", "string"}
        i = 0

        while i < len(tokens):
            lexema, _ = tokens[i]

            if lexema not in tipos_validos:
                i += 1
                continue

            tipo = lexema
            j = i + 1

            if j < len(tokens):
                nome, categoria = tokens[j]

                if categoria == "id":
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
                    arvore.update_table(self.escopo_global)

                    i = self._avancar_ate_fim_declaracao(tokens, j + 1)
                    continue

            i += 1

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
            elif lexema == ";" and profundidade_colchetes == 0:
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
            }:
                return i

            i += 1

        return i