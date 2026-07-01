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

    def proc_node(self):
        if self.prod == "leaf":
            return self.type, self.name

        elif self.prod == "VARDECL":
            self.type = self.children[0].type

        else:
            self.type = None

    def proc_tree(self):
        for child in self.children:
            proc_tree(child)

        proc_node(self)

    def update_table(self, scope):
        if self.prod == "leaf":
            scope.tabela.atualizar_tabela(self.name, self.type)
        else:
            for child in self.children:
                update_table(child, scope)
