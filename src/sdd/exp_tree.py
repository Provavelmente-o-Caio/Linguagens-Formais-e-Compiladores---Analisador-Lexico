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

def Node_Exp(prod, children, value, sym, name, self):
    self.prod = prod
    self.children = children
    self.value = value
    self.sym = sym
    self.name = name
    self.inh = None

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

