def Node_Dec(prod, children, type, name, self):
    self.prod = prod
    self.children = children
    self.type = type
    self.name = name
    
    def proc_node(self):
        if self.prod == 'leaf':
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
        if self.prod == 'leaf':
            scope.tabela.atualizar_tabela(self.name, self.type)
        else:
            for child in self.children:
                update_table(child, scope)


    '''
    def get_value(self):
        if self.type == 'leaf':
            return self.values[0]
        elif self.type == '+':
            return get_value(self.children[0]) + get_value(self.children[1])
        elif self.type == '*':
            return get_value(self.children[0]) * get_value(self.children[1])
        elif self.type == '-':
            return get_value(self.children[0]) - get_value(self.children[1])
        elif self.type == '/':
            return get_value(self.children[0]) / get_value(self.children[1])
        elif self.type == '%':
            return get_value(self.children[0]) % get_value(self.children[1])
        elif self.type == 'neg':
            return -get_value(self.children[0])
        elif self.type == 'pos':
            return +get_value(self.children[0])
    '''  