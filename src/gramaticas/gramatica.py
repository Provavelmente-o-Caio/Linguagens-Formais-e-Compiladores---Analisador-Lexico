from typing import List
from .simbolos import Terminal, NaoTerminal
from .producao import Producao


class Gramatica:
    """Representa uma gramática livre de contexto completa.
    
    Agrupa todos os componentes de uma GLC:
    - Produções
    - Símbolos terminais e não-terminais
    - Símbolo inicial
    
    Referência: Aho et al. (2006), Seção 4.1, Definição 4.1, pp. 191-194.
    
    Attributes:
        producoes: Lista de produções da gramática.
        terminais: Conjunto de símbolos terminais.
        nao_terminais: Conjunto de símbolos não-terminais.
        simbolo_inicial: Símbolo inicial da gramática.
    """
    
    def __init__(
        self,
        producoes: List[Producao],
        terminais: set[Terminal],
        nao_terminais: set[NaoTerminal],
        simbolo_inicial: NaoTerminal,
    ):
        """Inicializa uma gramática.
        
        Args:
            producoes: Lista de produções.
            terminais: Conjunto de símbolos terminais.
            nao_terminais: Conjunto de símbolos não-terminais.
            simbolo_inicial: Símbolo inicial.
        """
        self.producoes = producoes
        self.terminais = terminais
        self.nao_terminais = nao_terminais
        self.simbolo_inicial = simbolo_inicial

    def obter_producoes(self, nao_terminal: NaoTerminal) -> List[Producao]:
        """Obtém todas as produções com determinado não-terminal na cabeça.
        
        Args:
            nao_terminal: Não-terminal para buscar produções.
            
        Returns:
            Lista de produções com o não-terminal como cabeça.
        """
        return [p for p in self.producoes if p.cabeca == nao_terminal]
    
    def __repr__(self) -> str:
        """Representação textual da gramática."""
        linhas = [
            f"Gramática (S = {self.simbolo_inicial}):",
            f"  Produções: {len(self.producoes)}",
            f"  Não-terminais: {sorted([str(nt) for nt in self.nao_terminais])}",
            f"  Terminais: {sorted([str(t) for t in self.terminais])}",
        ]
        return "\n".join(linhas)
