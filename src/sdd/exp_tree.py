from __future__ import annotations


class NodeExp:
    def __init__(
        self,
        prod: str,
        children: list["NodeExp"] | None = None,
        value=None,
        sym: str | None = None,
        name: str | None = None,
    ):
        self.prod = prod
        self.children = children or []
        self.value = value
        self.sym = sym
        self.name = name

    @classmethod
    def leaf(cls, value=None, name: str | None = None, sym: str | None = None) -> "NodeExp":
        return cls("leaf", value=value, name=name, sym=sym)

    def proc_node(self):
        if self.prod == "leaf":
            return self.value

        if self.prod == "NUMEXPRESSION":
            termo = self.children[0].value
            resto = self.children[1]

            if resto.sym == "+":
                self.value = termo + resto.value
            elif resto.sym == "-":
                self.value = termo - resto.value
            else:
                self.value = termo

        elif self.prod == "NUMEXPRESSION'":
            if not self.children:
                self.sym = None
                self.value = 0
            else:
                operador = self.children[0].sym
                termo = self.children[1].value
                resto = self.children[2]

                self.sym = operador

                if resto.sym == "+":
                    self.value = termo + resto.value
                elif resto.sym == "-":
                    self.value = termo - resto.value
                else:
                    self.value = termo

        elif self.prod == "TERM":
            fator = self.children[0].value
            resto = self.children[1]

            if resto.sym == "*":
                self.value = fator * resto.value
            elif resto.sym == "/":
                self.value = fator / resto.value
            elif resto.sym == "%":
                self.value = fator % resto.value
            else:
                self.value = fator

        elif self.prod == "TERM'":
            if not self.children:
                self.sym = None
                self.value = 0
            else:
                operador = self.children[0].sym
                fator = self.children[1].value
                resto = self.children[2]

                self.sym = operador

                if resto.sym == "*":
                    self.value = fator * resto.value
                elif resto.sym == "/":
                    self.value = fator / resto.value
                elif resto.sym == "%":
                    self.value = fator % resto.value
                else:
                    self.value = fator

        elif self.prod == "UNARYEXPR":
            if len(self.children) == 2:
                operador = self.children[0].sym
                valor = self.children[1].value

                if operador == "-":
                    self.value = -valor
                elif operador == "+":
                    self.value = +valor
            else:
                self.value = self.children[0].value

        elif self.prod == "FACTOR":
            if len(self.children) == 3:
                self.value = self.children[1].value
            else:
                self.value = self.children[0].value

        elif self.prod == "LVALUE":
            self.value = None

        else:
            self.value = None

        return self.value

    def proc_tree(self):
        for child in self.children:
            child.proc_tree()

        return self.proc_node()
