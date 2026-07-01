from __future__ import annotations


class NodeDec:
    def __init__(
        self,
        prod: str,
        children: list["NodeDec"] | None = None,
        type_: str | None = None,
        name: str | None = None,
    ):
        self.prod = prod
        self.children = children or []
        self.type = type_
        self.name = name

    @classmethod
    def leaf(cls, name: str, type_: str | None = None) -> "NodeDec":
        return cls("leaf", type_=type_, name=name)

    def proc_node(self):
        if self.prod == "leaf":
            return self.type, self.name

        if self.prod == "TYPE":
            if self.children:
                self.type = self.children[0].name

        elif self.prod == "VARDECL":
            if self.children:
                self.type = self.children[0].type

        else:
            self.type = None

        return self.type, self.name

    def proc_tree(self):
        for child in self.children:
            child.proc_tree()

        return self.proc_node()

    def update_table(self, scope):
        if self.prod == "VARDECL":
            tipo = self.type

            for child in self.children:
                if child.prod == "leaf" and child.name is not None:
                    self._atualizar_tipo(scope, child.name, tipo)
                else:
                    child.update_table(scope)

        elif self.prod == "leaf":
            if self.name is not None and self.type is not None:
                self._atualizar_tipo(scope, self.name, self.type)

        else:
            for child in self.children:
                child.update_table(scope)

    def _atualizar_tipo(self, scope, nome: str, tipo: str | None):
        if tipo is None:
            return

        if hasattr(scope, "lookup"):
            entrada = scope.lookup(nome)
            entrada.tipo = tipo
            return

        if hasattr(scope, "atualizar_tabela"):
            scope.atualizar_tabela(nome, tipo)
            return

        if hasattr(scope, "atualizar_tipo"):
            scope.atualizar_tipo(nome, tipo)
            return

        raise TypeError("Objeto de escopo/tabela não suporta atualização de tipo")
