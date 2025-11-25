from typing import List, Union
from .simbolos import Terminal, NaoTerminal, Epsilon
from .gramatica import Gramatica


class HandlerGramatica:
    """Manipulador de gramáticas livres de contexto.
    
    Implementa algoritmos fundamentais para análise sintática:
    - FIRST: conjunto de terminais que podem iniciar strings derivadas de um símbolo
    - FOLLOW: conjunto de terminais que podem aparecer imediatamente após um não-terminal

    """
    
    def __init__(self, gramatica: Gramatica):
        """Inicializa o handler com a gramática.
        
        Args:
            gramatica: Objeto Gramatica contendo produções e símbolos.
        """
        self.gramatica = gramatica
        
        # Caches para FIRST e FOLLOW
        self.first_cache: dict[Union[Terminal, NaoTerminal], set[Terminal]] = {}
        self.follow_cache: dict[NaoTerminal, set[Terminal]] = {}


    def _calcular_first_sequencia(self, sequencia: List[Union[Terminal, NaoTerminal]]) -> set[Terminal]:
        """Calcula FIRST de uma sequência de símbolos Y1 Y2 ... Yk."""
        if not sequencia:
            return {Epsilon()}
        
        result = set()
        epsilon = Epsilon()
        
        for simbolo in sequencia:
            if isinstance(simbolo, Terminal):
                result.add(simbolo)
                return result
            
            # Não-terminal: pegar do cache
            first_simbolo = self.first_cache.get(simbolo, set())
            result.update(s for s in first_simbolo if s != epsilon)
            
            if epsilon not in first_simbolo:
                return result
        
        # Todos derivam epsilon
        result.add(epsilon)
        return result

    def calcular_firsts(self):
        """
        1. Se X ∈ T então FIRST(X) ={X}
        2. Se X ∈ N então
            (a) Se X ::= aY ∈ P então a ∈ FIRST(X)
            (b) Se X ::= ε ∈ P, então ε ∈ FIRST(X)
            (c) Se X ::= Y1Y2...Yk ∈ P, então FIRST(Y1) ∈ FIRST(X)
                i. Se ε ∈ FIRST(Y1), então FIRST(Y2) ∈ FIRST(X)
                ii. Se ε ∈ FIRST(Y2), ...
                iii. Se ε ∈ FIRST(Yk) e ... e ε ∈ FIRST(Y1) , então ε ∈ FIRST(X)
        """
        # Inicializar FIRST para todos X ∈ N
        for nt in self.gramatica.nao_terminais:
            self.first_cache[nt] = set()
        
        e = Epsilon()
        m = True

        # Iterar até ponto fixo
        while m:
            m = False
            
            for prod in self.gramatica.producoes:
                X = prod.cabeca
                corpo = prod.corpo
                prev_cache = len(self.first_cache[X])

                # Regra 2(b): Se X ::= ε ∈ P
                if not corpo:
                    self.first_cache[X].add(e)
                
                # Regra 2(a) e 2(c): Se X ::= Y1Y2...Yk ∈ P
                else:
                    for Yi in corpo:
                        if isinstance(Yi, Terminal):
                            # Regra 1: Se Yi ∈ T então Yi ∈ FIRST(X)
                            self.first_cache[X].add(Yi)
                            break
                        else:
                            # Yi ∈ N
                            # Regra 2(c): Adicionar FIRST(Yi) - {ε} a FIRST(X)
                            first_Yi = self.first_cache[Yi]
                            for s in first_Yi:
                                if s != e:
                                    self.first_cache[X].add(s)

                            # Se ε ∉ FIRST(Yi), parar
                            if e not in first_Yi:
                                break
                    else:
                        # Regra 2(c)(iii): Todos Yi derivam ε, então ε ∈ FIRST(X)
                        self.first_cache[X].add(e)
                
                if len(self.first_cache[X]) > prev_cache:
                    m = True
        
        return self.first_cache


    def get_first(self, simbolo: Union[Terminal, NaoTerminal]) -> set[Terminal]:
        """Retorna FIRST de um símbolo (usa cache se disponível)."""
        # Calcular todos os FIRSTs se cache vazio
        if not self.first_cache:
            self.calcular_firsts()

        return self.first_cache.get(simbolo, set()).copy()

    
    def calcular_follows(self):
        """
        1. Se S é o símbolo inicial da gramática, então $ ∈ FOLLOW(S)
        2. Se A ::= αBβ ∈ P e β 6= ε, então adicione FIRST(β) em
        FOLLOW(B)
        3. Se A ::= αB (ou A ::= αBβ, onde ε ∈ FIRST(β)) ∈ P, então
        adicione FOLLOW(A) em FOLLOW(B)
        FIRST(β) → FIRST(da sequência β)
        """
        # Inicializar FOLLOW para todos os não-terminais
        for nt in self.gramatica.nao_terminais:
            self.follow_cache[nt] = set()
        
        # Regra 1: Se S é o símbolo inicial, então $ ∈ FOLLOW(S)
        self.follow_cache[self.gramatica.simbolo_inicial].add(Terminal("$"))
        
        e = Epsilon()
        m = True
        
        # Iterar até ponto fixo
        while m:
            m = False
            
            # Para cada produção A ::= αBβ ∈ P
            for prod in self.gramatica.producoes:
                A = prod.cabeca
                corpo = prod.corpo
                
                # Para cada não-terminal B em corpo
                for i, B in enumerate(corpo):
                    if not isinstance(B, NaoTerminal):
                        continue
                    
                    prev_cache = len(self.follow_cache[B])
                    beta = corpo[i + 1:]  # Resto após B

                    if beta:
                        # Regra 2: Se A ::= αBβ ∈ P e β ≠ ε
                        # Adicionar FIRST(β) - {ε} a FOLLOW(B)
                        first_beta = self._calcular_first_sequencia(beta)
                        self.follow_cache[B].update(s for s in first_beta if s != e)
                        
                        # Regra 3: Se A ::= αBβ ∈ P onde ε ∈ FIRST(β)
                        # Adicionar FOLLOW(A) a FOLLOW(B)
                        if e in first_beta:
                            self.follow_cache[B].update(self.follow_cache[A])
                    else:
                        # Regra 3: Se A ::= αB ∈ P
                        # Adicionar FOLLOW(A) a FOLLOW(B)
                        self.follow_cache[B].update(self.follow_cache[A])
                    
                    if len(self.follow_cache[B]) > prev_cache:
                        m = True
        
        return self.follow_cache


    def get_follow(self, simbolo: NaoTerminal) -> set[Terminal]:
        """Retorna FOLLOW de um não terminal (usa cache se disponível)."""
        # Calcular todos os FIRSTs se cache vazio
        if not self.follow_cache:
            self.calcular_follows()

        return self.follow_cache.get(simbolo, set()).copy()


    def limpar_cache(self):
        """Limpa os caches de FIRST e FOLLOW."""
        self.first_cache.clear()
        self.follow_cache.clear()
