def Node_Exp(prod, children, value, sym, name, self):
    self.prod = prod
    self.children = children
    self.value = value
    self.sym = sym
    self.name = name
    
    def proc_node(self):
        if self.prod == 'leaf':
            return self.value, self.name
        
        elif self.prod == "NUMEXPRESSION":
            if self.children[1].sym == '+':
                self.value = self.children[0].value + self.children[1].value
            elif self.children[1].sym == '-':
                self.value = self.children[0].value - self.children[1].value
            elif self.children[1].sym == None:
                self.value = self.children[0].value
            
        elif self.prod == "NUMEXPRESSION'":
            if self.children[0].sym == '+':
                self.sym = '+'
            elif self.children[0].sym == '-':
                self.sym = '-'
            elif self.children[0].sym == None:
                self.sym = None  
                
            if self.children[1].sym == '+':
                self.value = self.children[0].value + self.children[1].value
            elif self.children[1].sym == '-':
                self.value = self.children[0].value - self.children[1].value
            elif self.children[1].sym == None:
                #self.value = self.children[0].value
                self.value = 0
            
        elif self.prod == "TERM":
            if self.children[1].sym == '*':
                self.value = self.children[0].value * self.children[1].value
            elif self.children[1].sym == '/':
                self.value = self.children[0].value / self.children[1].value
            elif self.children[1].sym == '%':
                self.value = self.children[0].value % self.children[1].value
            elif self.children[1].sym == None:
                self.value = self.children[0].value
        
        elif self.prod == "TERM'":
            if self.children[0].sym == '*':
                self.sym = '*'
            elif self.children[0].sym == '/':
                self.sym = '/'
            elif self.children[0].sym == '%':
                self.sym = '%'
            elif self.children[0].sym == None:
                self.sym = None  
            
            if self.children[1].sym == '*':
                self.value = self.children[0].value * self.children[1].value
            elif self.children[1].sym == '/':
                self.value = self.children[0].value / self.children[1].value
            elif self.children[1].sym == '%':
                self.value = self.children[0].value % self.children[1].value
            elif self.children[1].sym == None:
                #self.value = self.children[0].value
                self.value = 0
        
        elif self.prod == "UNARYEXP":
            if self.children[0].sym == '-':
                self.value = -self.children[1].value
            elif self.children[0].sym == '+':
                self.value = +self.children[1].value
            elif self.children[0].sym == None:
                self.value = self.children[0].value
            
        elif self.prod == "FACTOR":
            if self.children[0].sym == '(':
                self.value = self.children[1].value
            elif self.children[0].sym == None:
                self.value = self.children[0].value
        
        elif self.prod == "LVALUE":
            self.value = self.children[1].value
    
        else:
            self.value = None
            
    def proc_tree(self):
        for child in self.children:
            proc_tree(child)
            
        proc_node(self)
    
    '''
    def update_table(self, table):
            if self.prod == 'leaf':
                table[self.name] = self.value
            else:
                for child in self.children:
                    update_table(child, table)
    '''
        

    '''
    def get_value(self):
        if self.prod == 'leaf':
            return self.values[0]
        elif self.prod == '+':
            return get_value(self.children[0]) + get_value(self.children[1])
        elif self.prod == '*':
            return get_value(self.children[0]) * get_value(self.children[1])
        elif self.prod == '-':
            return get_value(self.children[0]) - get_value(self.children[1])
        elif self.prod == '/':
            return get_value(self.children[0]) / get_value(self.children[1])
        elif self.prod == '%':
            return get_value(self.children[0]) % get_value(self.children[1])
        elif self.prod == 'neg':
            return -get_value(self.children[0])
        elif self.prod == 'pos':
            return +get_value(self.children[0])
    '''  