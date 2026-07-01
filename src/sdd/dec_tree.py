def Node_Dec(prod, children, type, name, self):
    self.prod = prod
    self.children = children
    self.type = type
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
