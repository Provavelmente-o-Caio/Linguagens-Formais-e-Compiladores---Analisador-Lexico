def Node_Exp(prod, children, value, sym, name, self):
    self.prod = prod
    self.children = children
    self.value = value
    self.sym = sym
    self.name = name
    self.inh = None
    
    def proc_node(self):
        if self.prod == 'leaf':
            return self.value, self.name
        
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
        
        '''
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
                self.value = self.children[0].value
            
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
                self.value = self.children[0].value     
        '''
            
    def proc_tree(self):

        if self.prod == "NUMEXPRESSION":
            self.children[0].proc_tree()

            self.children[1].inh = self.children[0].value
            self.children[1].proc_tree()

            self.value = self.children[1].value
            return

        elif self.prod == "NUMEXPRESSION'":

            if len(self.children) == 0:          # ε
                self.value = self.inh
                self.sym = None
                return

            self.children[1].proc_tree()

            if self.children[0].sym == '+':
                self.children[2].inh = self.inh + self.children[1].value

            elif self.children[0].sym == '-':
                self.children[2].inh = self.inh - self.children[1].value

            self.children[2].proc_tree()

            self.value = self.children[2].value
            return

        elif self.prod == "TERM":

            self.children[0].proc_tree()

            self.children[1].inh = self.children[0].value
            self.children[1].proc_tree()

            self.value = self.children[1].value
            return

        elif self.prod == "TERM'":

            if len(self.children) == 0:
                self.value = self.inh
                self.sym = None
                return

            self.children[1].proc_tree()

            if self.children[0].sym == '*':
                self.children[2].inh = self.inh * self.children[1].value

            elif self.children[0].sym == '/':
                self.children[2].inh = self.inh / self.children[1].value

            elif self.children[0].sym == '%':
                self.children[2].inh = self.inh % self.children[1].value

            self.children[2].proc_tree()

            self.value = self.children[2].value
            return

        # all remaining productions
        for child in self.children:
            child.proc_tree()

        self.proc_node()
    
    '''
    def proc_tree(self): 
        for child in self.children: 
            proc_tree(child) 
            
        proc_node(self)
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