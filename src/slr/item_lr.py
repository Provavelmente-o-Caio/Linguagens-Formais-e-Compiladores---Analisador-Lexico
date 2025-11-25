from dataclasses import dataclass
from typing import Union
from src.gramaticas import Producao, Terminal, NaoTerminal


@dataclass(frozen=True)
class ItemLR:
    """Representa um item LR(0): A ::= α·β
    
    Um item LR(0) indica uma posição de parsing dentro de uma produção.
    O ponto (·) marca até onde foi reconhecido.
    
    Referência: Aho et al. (2006), Seção 4.6.2, pp. 241-246.
    
    Attributes:
        producao: Produção da gramática (A ::= αβ)
        posicao: Posição do ponto na produção (|α|)
    """
    producao: Producao
    posicao: int
    
    def __str__(self) -> str:
        """Representação em string: A ::= α·β"""
        corpo = self.producao.corpo
        prev = " ".join(str(s) for s in corpo[:self.posicao])
        post = " ".join(str(s) for s in corpo[self.posicao:])

        if prev and post:
            return f"{self.producao.cabeca} ::= {prev} · {post}"
        elif prev:
            return f"{self.producao.cabeca} ::= {prev} ·"
        elif post:
            return f"{self.producao.cabeca} ::= · {post}"
        else:
            return f"{self.producao.cabeca} ::= ·"
    
    def simbolo_apos_ponto(self) -> Union[Terminal, NaoTerminal, None]:
        """Retorna o símbolo imediatamente após o ponto, ou None se no final."""
        if self.posicao < len(self.producao.corpo):
            return self.producao.corpo[self.posicao]
        return None

    def esta_completo(self) -> bool:
        """Verifica se o item está completo (ponto no final)."""
        return self.posicao >= len(self.producao.corpo)
    
    def avancar(self) -> 'ItemLR':
        """Retorna novo item com ponto avançado uma posição."""
        return ItemLR(self.producao, self.posicao + 1)
